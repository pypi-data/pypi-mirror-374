from typing import Any
from . .common_imports import *
from . .independent import Tokenization
from . .model.layers import Block, RoPE
from . .model.model import Model
from . ._utils import key
from .predict import SetUpAPI

@partial(jax.jit, static_argnums=(0,))
def call_block_low(block, params, x, mask, s_pos, k, v):
    return block.apply({'params':params}, x, mask, False, s_pos, k, v)

class KV_caching:
    def __init__(self, model, top_p=0.9, temperature=1.0) -> None:
        self.block = Block(num_heads = model.data['num_heads'],
                           attention_dim= model.data['attention_dim'],
                           ff_dim= model.data["ff_dim"],
                           dropout_rate= model.data['dropout_rate'],
                           flash_attn= False,attn_chunks= 1,
                           gqa_repeats=model.data.get('gqa_repeats', 1),
                           res_scale=model.data.get('res_scale', 1),
                           KV_cache=True)
        self.params = model.params
        self.num_blocks = model.num_blocks
        self.model = model
        self.top_p = top_p
        self.temp = temperature

    def call_emb(self,x):
         return self.model.model_struct.apply(self.params, x, method=Model.embed_call)
    
    @partial(jax.jit,static_argnums=(0,))
    def apply_ropeEmb(self, x, pos):
        return RoPE(self.call_emb(x[None,:]),pos)
    
    def get_mask(self, x):
        return self.model.model_struct.apply(self.params, jnp.ones(x.shape), method= Model.process_mask)
    
    @partial(jax.jit,static_argnums=(0,))
    def apply_last_layer(self, x, key):
        logits = jnp.squeeze(self.model.model_struct.apply(self.params, x, method=Model.last_layer_fn))[None,:]/self.temp
        probs = jax.nn.softmax(logits.astype(jnp.float32))
        sorted_probs = jnp.sort(probs, axis=-1)[..., ::-1]

        cum_probs = jnp.cumsum(sorted_probs, axis=-1)
        mask = cum_probs > self.top_p

        cutoff = jnp.argmax(mask, axis=-1)
        cutoff = jnp.where(mask.any(axis=-1), cutoff, sorted_probs.shape[-1] - 1)

        threshold = sorted_probs[0, cutoff[0]]

        filtered_probs = jnp.where(probs < threshold, 0.0, probs)
        filtered_probs = filtered_probs / jnp.sum(filtered_probs, axis=-1, keepdims=True)

        # Sample one token
        sampled_token = jax.random.categorical(key, jnp.log(filtered_probs), axis=-1)
        return sampled_token

    def call_block(self,x,mask, block_pos,s_pos, k, v):
        return call_block_low(self.block, self.params['params'][f'blocks_{block_pos}'], x, mask, s_pos,k, v)
    
    def __call__(self, x,max_len = 8):
        x = jnp.array(x, dtype=jnp.uint16)
        total_max_len = len(x) + max_len
        padding_len = total_max_len - len(x)
        """ Ok so here we are keep x as len(shape) = 1 mmh?"""
        k_cache = [jnp.zeros((1, total_max_len, self.model.data['attention_dim']//self.model.data.get('gqa_repeats',1)),dtype=self.model.model_struct.dtype) for _ in range(self.num_blocks)]
        v_cache = [jnp.zeros((1, total_max_len, self.model.data['attention_dim']//self.model.data.get('gqa_repeats',1)),dtype=self.model.model_struct.dtype) for _ in range(self.num_blocks)]

        x = jnp.concatenate([x, jnp.full((padding_len,), jnp.nan)])
        mask = jax.lax.transpose(self.get_mask(jnp.ones((1,total_max_len),dtype=jnp.uint8)),(2,0,1,3))
        for i in range(total_max_len-1):
            x_buffer = self.apply_ropeEmb(x[i:i+1].astype(jnp.uint16), i)
            for j in range(self.num_blocks):
                x_buffer, k_cache[j], v_cache[j] = self.call_block(x_buffer, mask[i][:,:,None,:],j,i,k_cache[j],v_cache[j])
            if bool(jnp.isnan(x[i+1:i+2])):
                predicted_token = self.apply_last_layer(x_buffer, key.next_key())
                x_ = jnp.array([int(predicted_token[0])],dtype=jnp.int32)
                x = x.at[i+1].set(x_[0])
                yield x_
