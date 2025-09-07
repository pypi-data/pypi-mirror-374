from .layers import *
import flax.serialization
from . ._errors import *
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from tqdm import tqdm
from . .independent import *
from . ._errors import *
from . .common_imports import *
from . ._utils import TrainRailGuard, get_kv, tree_fn
from . .trainerNeval.eval import stat_fn
from . .data.data_low import make_mask_low
import math
from collections import deque

from rich.live import Live
from rich.table import Table
from rich.progress import Progress
from rich.console import Group

import gc
### Constants
rng = jax.random.PRNGKey(0)

class Model(nn.Module):
    num_heads: int | tuple
    attention_dim: int
    vocab_size: int
    num_blocks: int
    ff_dim: int
    dropout_rate: float
    emb_splt: int
    max_len: int = 8192
    attn_chunks: int = 1
    gqa_repeats: int = 1
    use_fash_attention: bool = False
    emb_scaling_factor: float = 1.0
    res_scale: float = 1.0
    emb_init_range: float | None = None
    param_init_rage: float =  0.002
    dtype: jnp.dtype = jnp.float32

    def setup(self):
        if self.emb_scaling_factor != 1:
            print("WARNING: This model is using emb_scale set to a number than 1 and most of the external functions like KV caching won't work if so")
        self.emb_scale = jnp.array([self.emb_scaling_factor], dtype=jnp.float32)
        self.emb = nn.Embed(
             num_embeddings=self.vocab_size,
             features=self.attention_dim,
             embedding_init=nn.initializers.normal(stddev= 1/math.sqrt(self.attention_dim) if self.emb_init_range is None else self.emb_init_range),
             dtype=self.dtype
             )
        
        if isinstance(self.num_heads, tuple):
            if len(self.num_heads) == self.num_blocks:
                pass
            else:
                print("Using flash attention") if self.use_fash_attention else None
                raise ModelHpMismatch(f"Model needs a list of heads which is the length of the number of blocks. Here number of heads {len(self.num_heads)} and Number of blocks {self.num_blocks} are not equal.")
            self.blocks = [Block(num_heads=i,attention_dim=self.attention_dim,ff_dim=self.ff_dim,dropout_rate=self.dropout_rate,flash_attn=self.use_fash_attention,gqa_repeats=self.gqa_repeats, attn_chunks=self.attn_chunks, res_scale=self.res_scale, weight_init_range=self.param_init_rage, dtype=self.dtype)for i in self.num_heads]
        elif isinstance(self.num_heads, int):
            self.blocks = [Block(num_heads=self.num_heads,attention_dim=self.attention_dim,ff_dim=self.ff_dim,dropout_rate=self.dropout_rate,flash_attn=self.use_fash_attention, gqa_repeats=self.gqa_repeats, attn_chunks=self.attn_chunks, res_scale=self.res_scale, weight_init_range=self.param_init_rage, dtype=self.dtype)for _ in range(self.num_blocks)]
        else:
             raise DebugError(f"Bruh! What? So num head is not a list of a string? It's a {self.num_heads}")
    
    def __call__(self, x, mask, training=True):
        return self.last_layer_fn(self.blocks_fn(self.embed_call(x), x, mask, training))

    def process_mask(self,mask):
        shape_check(
            (mask, 2, None, 'mask')
        )
        if self.use_fash_attention:
            return mask
        else:
            batch_size, seq_len = mask.shape

            # Create causal mask (lower triangular matrix)
            causal_mask = jnp.tril(jnp.ones((seq_len, seq_len)))

            # Reshape padding mask and apply to causal mask
            mask = mask[:, None, :]  # (batch_size, 1, seq_len)
            mask_sq = causal_mask[None, :, :] * mask  # (batch_size, seq_len, seq_len)
            mask_sq = jnp.transpose(mask_sq, (0, 2, 1)) * mask
            mask_sq = jnp.transpose(mask_sq, (0, 2, 1))[:, None, :]
            #mask_sq = jnp.broadcast_to(mask_sq, (batch_size, self.num_heads, seq_len, seq_len))
            return jnp.array(mask_sq).astype(jnp.bool)
    
    def last_layer_fn(self,x):
        return lax_matmul(x, self.emb.embedding, (2,), (1,),(),(P("data", None, None),P("model", None)))
    
    def embed_call(self,x):
        return RoPE(x=self.emb(x.astype(jnp.uint16))).astype(jnp.bfloat16)
    
    def blocks_fn(self, x, x_, mask, training=True):
        mask = lax.cond(
            jnp.array(training,dtype=jnp.bool_),
            lambda _: make_mask_low(x_),
            lambda _: self.process_mask(mask),
            operand=None
        )

        x = x.astype(jnp.bfloat16)
        for i in self.blocks:
            x = i(x,mask,training)
        return x
    
    def prim_run(self,x,mask, training=True):
        return self.blocks_fn(self.embed_call(x), x, mask, training)
        

class ModelManager():
    @debug_state.trace_func
    def __init__(
        self,
        num_heads: tuple,
        attention_dim: int,
        vocab_size: int,
        num_blocks: int,
        ff_dim: int,
        dropout_rate: float,
        max_len: int,
        emb_splt: int = 256,
        attn_chunks: int = 1,
        dtype=None,
        possible_opt_path: str = "",
        *args,
        **kwargs
    ) -> None:
        self.key = jax.random.PRNGKey(0)
        self.num_blocks = num_blocks
        self.model_struct = Model(num_heads, attention_dim, vocab_size, num_blocks, ff_dim, dropout_rate, max_len,
                                  emb_splt, attn_chunks, **kwargs,dtype= dtype)
        self.params = self.model_struct.init(self.key,jax.random.normal(self.key,(8, attn_chunks)),jnp.ones((8, attn_chunks))) 
        if dtype is not None:
            self.params = tree_fn.convert_tree(dtype,self.params)
        self.optimizer = None
        self.possible_opt_path = possible_opt_path

        self.data = {
            "num_heads":num_heads,
            "attention_dim":attention_dim,
            "vocab_size":vocab_size,
            "num_blocks":num_blocks,
            "ff_dim":ff_dim,
            "dropout_rate":dropout_rate,
            'possible_opt_path':possible_opt_path,
            "max_len":max_len,
            "attn_chunks":attn_chunks
        }
        self.data = self.data | kwargs
        gc.collect()

    def __call__(self,input,mask):
        shape_check(
            (input, 2, None, 'input'),
            (mask, 2, None, 'mask')
        )
        shape_match(
            (input,'input'),
            (mask, 'mask')
        )
        return self.model_struct.apply(self.params,input,mask,rngs={"dropout": self.key},training=False)
    
    @partial(jax.jit,static_argnums=(0))
    def jax_call(self,input,mask):
        shape_check(
            (input, 2, None, 'input'),
            (mask, 2, None, 'mask')
        )
        shape_match(
            (input,'input'),
            (mask, 'mask')
        )
        return self.model_struct.apply(self.params,input,mask,rngs={"dropout": self.key},training=False)
    

    @property
    def trainable_variables(self):
        return self.params
    
    @property
    def key_bruh(self):
        self.key, subkey = jax.random.split(self.key)
        return subkey
    
    @debug_state.trace_func
    def training_setup(self,optimizer,data,state_path=""):
        self.optimizer = Optimizer(optimizer,self.params,data)
        if state_path == "":
            self.optimizer.load(self.possible_opt_path)
        else:
            self.optimizer.load(state_path)
        self.grad_fn = jax.value_and_grad(loss_fn)
        return self.optimizer.lr_schedule
    
    @debug_state.trace_func
    def train_batch(self,x,mask,y,step, **kwargs):
        key = self.key_bruh
        loss, self.params, self.optimizer.state, [N_per_layer, grad_norm], [A_per_layer, abs_mean] = BatchTrain(self.params, self.grad_fn, self.model_struct, x, mask, y, key, self.optimizer.optimizer, self.optimizer.state, self.chunks, kwargs.get("grad_accum", 1))
        self.stats['grad_norm'] = jax.tree_util.tree_map(
            lambda avg, new: avg + (float(new) - avg) / step,
            self.stats['grad_norm'],
            N_per_layer
        )

        self.stats['abs_mean'] = jax.tree_util.tree_map(
            lambda avg, new: avg + (float(new) - avg) / step,
            self.stats['abs_mean'],
            A_per_layer
        )
        return loss, grad_norm, abs_mean
    
    @debug_state.trace_func
    def save_model(self,name,opt_state=True):
        os.makedirs(name, exist_ok=True)
        with open(os.path.join(name, "good_stuff.pkl"), "wb") as f:
            f.write(flax.serialization.to_bytes(self.trainable_variables))

        with open(os.path.join(name, "understanding_good_stuff.json"),"w") as f:
            json.dump(self.data, f, indent=2)
        
        if (opt_state) and (self.optimizer is not None):
            with open(os.path.join(name, "make_stuff_better.pkl"), "wb") as f:
                f.write(flax.serialization.to_bytes(self.optimizer.state))

    @debug_state.trace_func
    def batch_it(self, x, mask, y, batch_size, x_eq_y=True):
        dataset = Flax_ds(x_eq_y)
        dataset.load_data(x,mask,y)
        dataset.batch_it_(batch_size=batch_size)
        return dataset

    @debug_state.trace_func
    def train(self,x,mask,y,epochs,batch_size,optimizer,lr_data,val_x=None,val_mask=None,val_y=None,val_step=100,updates_in=1,avg_mem=25,state_path=None,chunks=1,cp_after=None, chunked_training=False, total_steps=None, *args, **kwargs):
        # The training function will be here soon
        pass
    
    @debug_state.trace_func
    def grad_stats_show(self, attr = 'abs_mean',skip_layers=[],skip_all=[]):
        plt.figure(figsize=(12, 6))
        filtered = [
            (names, values)
            for names, values in get_kv(self.stats[attr]).items()
            if names.split("/")[-1] not in skip_all and names not in skip_layers
        ]
        [plt.bar(names, values) for names, values in filtered]
        plt.xticks(rotation=90)
        plt.ylabel(f'Gradient Stat ({attr})')
        plt.xlabel('Layer Name')
        plt.title('Layer-wise Gradient Stats')
        plt.tight_layout()
        plt.show()
    
    def param_stats_show(self,path="model_param_stats"):
        tree = tree_fn.apply_tree_fn(self.params, stat_fn)
        stats = tree_fn.apply_tree_fn(tree, lambda x: float(x))
        with open(path, "w") as f:
            json.dump(stats, f, indent=4)

    @debug_state.trace_func
    def summary(self):
        def count_params(params):
            total = 0
            if hasattr(params, "values"):
                for value in params.values():
                    if isinstance(value, dict):
                        total += count_params(value)
                    elif hasattr(value, 'size'):
                        total += value.size
            else:
                total = 1
            return total
        
        for i in list(self.trainable_variables['params'].keys()):
            print(f"{i} :{count_params(self.trainable_variables['params'].get(i, {})):,}")
        print("-------------------")
        print(f"Total :{count_params(self.trainable_variables['params']):,}")
        gc.collect()
    
    @debug_state.trace_func
    def change_precision(self,dtype):
        self.params = jax.tree_util.tree_map(lambda x: x.astype(dtype),self.params)
        gc.collect()

    @property
    def precision(self):
        type_tree = jax.tree_util.tree_map(lambda x: x.dtype,self.model)
        types = jax.tree_util.tree_leaves(type_tree)
        if len(set(types)) == 1:
            print(f"Model dtype:{types[0]}")
        else:
            print("Model contains mixed dtypes")
        gc.collect()



### Test stuff for now ok?
### TODO: Bruh your forgot to get the better predict from googel collab ;-;

@debug_state.trace_func
def plot(losses, num_points=1000, chop_off=100, sigma=2):
    # Validation
    if len(losses) < chop_off:  # Ensure enough data remains
        raise ValueError("Not enough data points after chopping")
    
    # Remove initial unstable period
    chopped_losses = losses[chop_off:]
    
    # Gaussian smoothing (preserves trends better than moving average)
    smoothed = gaussian_filter1d(chopped_losses, sigma=sigma, mode='nearest')
    
    # Adaptive downsampling - show peaks/valleys while limiting points
    step = max(1, len(smoothed) // num_points)
    sampled_indices = np.arange(0, len(smoothed), step)
    
    # Original batch numbers need adjustment after chopping
    original_batches = np.arange(len(losses))[chop_off:]
    sampled_batches = original_batches[sampled_indices]
    sampled_losses = smoothed[sampled_indices]

    # Plot with improved visualization
    plt.figure(figsize=(12, 6))
    plt.plot(sampled_batches, sampled_losses, 
             linestyle='-', 
             linewidth=1.5,
             color='royalblue',
             alpha=0.8,
             label=f'Smoothed (σ={sigma})')
    
    # Add faint original line for reference
    plt.plot(original_batches, chopped_losses, 
             alpha=0.15, 
             color='gray',
             linewidth=0.5,
             label='Original')
    
    plt.xlabel('Batch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title(f'Loss Curve [First {chop_off} batches chopped]', fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()