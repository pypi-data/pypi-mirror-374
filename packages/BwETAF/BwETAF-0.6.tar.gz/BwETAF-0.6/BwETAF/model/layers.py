from typing import Any
from . .common_imports import *
from . ._utils import lax_matmul
from jax import lax
from . ._errors import shape_check, shape_match
try:
    from flash_attention_jax import flash_attention
except:
    print("BwETAF: No flash attention module imported")
from . ._errors import ModelHpMismatch, UnusableModule


class PosEnc(nn.Module):
    dim : int
    dtype: jnp.dtype = jnp.bfloat16

    @nn.compact
    def __call__(self, x):
        _ , sequence_length, _ = x.shape

        # Compute div term once (avoiding repeated `exp` calls)
        div_term = jnp.exp(-jnp.arange(0, self.dim, 2) * (jnp.log(10000.0) / self.dim)).astype(self.dtype)

        # Compute positions in one step (efficiently broadcasting)
        position = jnp.arange(sequence_length)[:, None] * div_term  # (seq_len, emb_dim/2)

        # Directly compute sine & cosine, then interleave them
        pos_enc = jnp.zeros((sequence_length, self.dim),dtype=self.dtype)
        pos_enc = pos_enc.at[:, 0::2].set(jnp.sin(position)).astype(self.dtype)
        pos_enc = pos_enc.at[:, 1::2].set(jnp.cos(position)).astype(self.dtype)

        # Expand for batch & return
        return x + pos_enc[None, :, :]

def RoPE(x, pos=None):
    """
    Applies Rotary Position Embedding (RoPE) to input tensors.
    
    Args:
        x: Input tensor of shape (b, s, d) when pos=None, or (1, 1, d) when pos is an integer.
        pos: 
            - None: Apply RoPE for positions 0 to s-1 (batched mode)
            - int: Apply RoPE for the specified position (single token mode)
    
    Returns:
        Tensor with RoPE applied, same shape as x.
    """
    shape_check(
        (x, 3, None, 'x'),
    )
    b, s, d = x.shape
    dim = d // 2
    
    # Precompute inverse frequencies (constant for given d)
    inv_freq = 10000.0 ** (-jnp.arange(0, dim, 1, dtype=jnp.float32) / dim)
    inv_freq = inv_freq.astype(x.dtype)  # Match input dtype
    
    # Generate position tensor based on mode
    if pos is None:
        # Batched sequence mode - positions [0, 1, ..., s-1]
        positions = jnp.arange(s, dtype=x.dtype)[None, :, None]  # (1, s, 1)
    else:
        # Single token mode - specified position
        positions = jnp.array([[pos]], dtype=x.dtype)  # (1, 1, 1)
    
    # Compute sinusoids
    freqs = positions * inv_freq  # (1, s, dim) or (1, 1, dim)
    cos = jnp.cos(freqs)
    sin = jnp.sin(freqs)
    
    # Split features into halves
    x1, x2 = x[..., :dim], x[..., dim:2*dim]
    
    # Apply rotation
    x1_rot = x1 * cos - x2 * sin
    x2_rot = x2 * cos + x1 * sin
    
    # Combine rotated features with unmodified tail (if d is odd)
    rotated = jnp.concatenate([x1_rot, x2_rot], axis=-1)
    if d % 2 == 1:
        rotated = jnp.concatenate([rotated, x[..., -1:]], axis=-1)
    
    return rotated

class Attention(nn.Module):
    num_heads: int
    d_model: int
    chunks: int = 1
    duplicates: int = 1
    KV_cache: bool = False
    weight_init_range: float = 0.02
    dtype: jnp.dtype = jnp.bfloat16

    def setup(self):
        if self.d_model % self.num_heads != 0:
            raise ModelHpMismatch("d_model must be divisible by num_heads")
        if self.num_heads % self.duplicates != 0:
            raise ModelHpMismatch('Number of heads must be divisible by GQA duplicates')
        
        # ===== GQA calc =====
        self. KV_group_d = self.d_model // self.duplicates

        self.depth = self.d_model // self.num_heads
        self.k_dense = lax_Dense(features=self.KV_group_d, weight_init_range=self.weight_init_range, dtype=self.dtype,use_bias=False)
        self.q_dense = lax_Dense(features=self.d_model, weight_init_range=self.weight_init_range, dtype=self.dtype,use_bias=False)
        self.v_dense = lax_Dense(features=self.KV_group_d, weight_init_range=self.weight_init_range, dtype=self.dtype,use_bias=False)
        self.d_out = lax_Dense(features=self.d_model,weight_init_range=self.weight_init_range, dtype=self.dtype)

        self.RoPE_int = lambda x, pos=None: RoPE(x ,pos)

    def __call__(self, x, mask, pos = 0, cache_k=[], cache_v=[]):
        shape_check(
            (x, 3, (None, None, self.d_model),'x'),
            (mask, 4, None, 'mask')
        )
        if not self.KV_cache:
            q = self.prep_for_attn(self.RoPE_int(self.q_dense(x)))
            k = self.prep_for_attn(self.RoPE_int(self.k_dense(x)),normal=False)
            v = self.prep_for_attn(self.v_dense(x), normal=False)

            return self.d_out(chunked_kqv_dp(k,q,v,mask,self.chunks))
        else:
            shape_match(
                (cache_k, 'cache_k'),
                (cache_v, 'cache_v')
            )
            q = self.q_dense(x)
            q = self.RoPE_int(q, pos)
            q = self.prep_for_attn(q)

            k = self.k_dense(x)
            k = self.RoPE_int(k, pos)
            cache_k = lax.dynamic_update_slice(cache_k, k, (0, pos, 0))
            k = self.prep_for_attn(cache_k, normal=False)

            v = self.v_dense(x)
            cache_v = lax.dynamic_update_slice(cache_v, v, (0, pos, 0))
            v = self.prep_for_attn(cache_v, normal=False)
            return self.d_out(chunked_kqv_dp(k,q,v,mask,self.chunks)), cache_k, cache_v
        
    def prep_for_attn(self, x, normal= True):
        b, s = x.shape[0], x.shape[1]
        if normal:
            return jax.lax.transpose(x.reshape(b, s, self.num_heads, self.depth), (0, 2, 1, 3))
        else:
            return jnp.repeat(jax.lax.transpose(x.reshape(b, s, self.num_heads//self.duplicates, self.depth), (0, 2, 1, 3)), repeats=self.duplicates, axis=1)
            


def chunked_kqv_dp(k,q,v,m,chunks):
    shape_check(
        (k, 4, None, 'k'),
        (q, 4, None, 'q'),
        (v, 4, None, 'v')
    )
    shape_match(
        (k,'k'),
        (v,'v')
    )
    batch_size, num_heads,seq_len, depth = k.shape
    chunk_size = q.shape[2]//chunks

    assert seq_len % chunks == 0, f"Seq len must divisible with number of chunks, currently it's {seq_len}"

    q = jax.lax.reshape(q,(batch_size,num_heads,chunks,chunk_size,depth))
    q = jax.lax.transpose(q, (2, 0, 1, 3, 4))

    mask_chunked = lax.reshape(m,(batch_size,1,chunks,chunk_size,seq_len))
    mask_chunked = jax.lax.transpose(mask_chunked, (2, 0, 1, 3, 4))
    @jax.remat
    def chunk_fn(_ ,x):
        q, mask = x
        logits = lax_matmul(q,k,(3,),(3,),(0,1),(P("data", "model", None, None),P("data", "model", None, None))) /jnp.sqrt(depth)

        logits = jnp.where(mask, logits, -1e9)

        attn_weights = jax.nn.softmax(logits, axis=-1)
        attn_output = lax_matmul(attn_weights, v, (3,), (2,), (0, 1),(P("data", "model", None, None),P("data", "model", None, None)))

        # Concatenate heads
        attn_output = lax.transpose(attn_output, (0, 2, 1, 3))  # (batch, seq_len, num_heads, depth)
        attn_output = lax.reshape(attn_output,(batch_size, chunk_size, depth*num_heads)) # (batch, seq_len, d_model)
        return None, attn_output
    
    return jnp.concatenate(jax.lax.scan(chunk_fn,None,(q,mask_chunked))[1],axis=1)


class FlashAttentionLayer(nn.Module):
    num_heads: int
    d_model: int
    use_RoPE: bool = False
    dtype: jnp.dtype = jnp.bfloat16

    def setup(self):
        assert self.d_model % self.num_heads == 0, "d_model must be divisible by num_heads"
        self.depth = self.d_model // self.num_heads
        self.k_dense = lax_Dense(features=self.d_model, dtype=self.dtype,use_bias=False)
        self.q_dense = lax_Dense(features=self.d_model, dtype=self.dtype,use_bias=False)
        self.v_dense = lax_Dense(features=self.d_model, dtype=self.dtype,use_bias=False)
        self.d_out = lax_Dense(features=self.d_model,dtype=self.dtype)

    def __call__(self, x, mask):
        batch_size, seq_len, _ = x.shape

        q = self.q_dense(x).reshape(batch_size, seq_len, self.num_heads, self.depth)
        k = self.k_dense(x).reshape(batch_size, seq_len, self.num_heads, self.depth)
        if self.use_RoPE:
            q = RoPE(q)
            k = RoPE(k)

        q = jax.lax.transpose(q, (0, 2, 1, 3)).astype(jnp.float32)
        k = jax.lax.transpose(k, (0, 2, 1, 3)).astype(jnp.float32)
        v = jax.lax.transpose(self.v_dense(x).reshape(batch_size, seq_len, self.num_heads, self.depth), (0, 2, 1, 3)).astype(jnp.float32)
        attn_weights = flash_attention(q, k, v, mask).astype(self.dtype)

        attn_weights = lax.transpose(attn_weights, (0, 2, 1, 3)) # (batch, seq_len, num_heads, depth)
        attn_weights = lax.reshape(attn_weights,(batch_size, seq_len, self.d_model)) # (batch, seq_len, d_model)
        return self.d_out(attn_weights)
    

def softmax_lax(x, axis=-1):
    x_max = lax.max(x, axes=(axis,), keepdims=True)
    x = lax.sub(x, lax.stop_gradient(x_max))  # for numerical stability
    exp_x = lax.exp(x)
    sum_exp_x = lax.reduce(exp_x, 0.0, lax.add, axes=(axis,), keepdims=True)
    return lax.div(exp_x, sum_exp_x)


class Block(nn.Module):
    num_heads : int
    attention_dim : int
    ff_dim : int
    dropout_rate : float
    flash_attn: bool = False
    attn_chunks: int = 1
    gqa_repeats: int = 1
    res_scale: float = 1
    KV_cache: bool = False
    weight_init_range: float = 0.02
    dtype: jnp.dtype = jnp.bfloat16

    def setup(self):
        if self.flash_attn:
            print("BwETAF WARNING: you are trying to use flash attn which is currently not working")
        self.ln1 = RMSNorm(dtype=self.dtype)
        self.attn = nn.remat(FlashAttentionLayer)(self.num_heads, self.attention_dim, self.KV_cache,dtype=self.dtype) if self.flash_attn else nn.remat(Attention)(self.num_heads, self.attention_dim, chunks=self.attn_chunks,duplicates=self.gqa_repeats, KV_cache=self.KV_cache,weight_init_range= self.weight_init_range, dtype=self.dtype)
        self.dp1 = nn.Dropout(self.dropout_rate)
        self.ln2 = RMSNorm(dtype=self.dtype)
        self.d1 = lax_Dense(self.ff_dim*2, weight_init_range=self.weight_init_range, dtype=self.dtype)
        self.d2 = lax_Dense(self.attention_dim, weight_init_range=self.weight_init_range, dtype=self.dtype)

        
    def __call__(self, x_inp, mask, train=True, pos=0, cache_k=None,cache_v=None):
        shape_check(
            (x_inp, 3,(None, None, self.attention_dim),'x'),
            (mask, 4, None, 'mask')
        )
        x = self.ln1(x_inp)
        if self.KV_cache:
            shape_match(
                (cache_k, 'cache_k'),
                (cache_v, 'cache_v')
            )
            x,k_cache,v_cache = self.attn(x, mask, pos, cache_k, cache_v)
        else:
            x = self.attn(x, mask)

        x = self.dp1(x, deterministic=not train)
        x_inp = x + x_inp

        # Pre-LN before FFN
        x = self.ln2(x_inp)  
        x = self.d1(x)
        key, gate = jnp.split(x, 2, axis=-1)
        x = self.d2(nn.swish(gate) * key)

        if self.KV_cache:
            return x + x_inp, k_cache, v_cache
        else:
            return x + x_inp


class lax_Dense(nn.Module):
    features : int
    weight_init_range: float = 0.02
    dtype: jnp.dtype = jnp.bfloat16
    use_bias: bool = True

    @nn.compact
    def __call__(self,x) -> Any:
        w = self.param('w',nn.initializers.normal(stddev=self.weight_init_range),(x.shape[-1],self.features),dtype=self.dtype)
        if self.use_bias:
            b = self.param('b', nn.initializers.zeros, (1, 1, self.features), dtype=self.dtype)

        if self.use_bias:
            return jax.lax.add(lax_matmul(x,w,(2),(0),()),b)
        else:
            return lax_matmul(x,w,(2),(0),())


class RMSNorm(nn.Module):
    eps: float = 1e-8
    dtype: jnp.dtype = jnp.bfloat16

    @nn.compact
    def __call__(self, x):
        rms = jnp.sqrt(jnp.mean(x ** 2, axis=-1, keepdims=True) + self.eps)
        scale = self.param('scale', nn.initializers.ones, (x.shape[2],),dtype=self.dtype)
        return ((x / rms) * scale).astype(self.dtype)

class FactorizedEmbed(nn.Module):  # TODO: Do something about this.... I don't think it's gonna make it so break it like not handled sharding specs
    vocab_size: int
    embed_dim: int
    factor_dim: int = 0
    dtype: jnp.dtype = jnp.bfloat16

    def setup(self):
        raise UnusableModule("The FactorizedEmbed layer is still underdevelopment and might break under certain conditions... Use at your own risk")
        if self.factor_dim == 0:
            self.embed_factor = nn.Embed(self.vocab_size, self.embed_dim,dtype=self.dtype)
        else:
            self.embed_factor = nn.Embed(self.vocab_size, self.factor_dim,dtype=self.dtype)
            self.P_w = self.param('w',nn.initializers.normal(stddev=0.02),(self.factor_dim,self.embed_dim),dtype=self.dtype)

    def __call__(self, x):
        if self.factor_dim == 0:
            return self.embed_factor(x)
        else:
            x = self.embed_factor(x)
            return lax_matmul(x,self.P_w,(2),(0),())
    
    def rev_call(self,x):
        if self.factor_dim == 0:
            return lax_matmul(x, self.embed_factor.embedding, (2,), (1,),())
        else:
            x = lax_matmul(x,self.P_w,(2),(1),())
            return lax_matmul(x, self.embed_factor.embedding, (2,), (1,),())
    