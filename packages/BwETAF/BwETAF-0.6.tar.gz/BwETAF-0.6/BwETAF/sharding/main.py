from . .common_imports import *
from jax.sharding import Mesh, PartitionSpec as P
from . ._utils import tree_fn, TrainRailGuard
from jax.sharding import NamedSharding
from jax.experimental.pjit import pjit
from . ._utils import val_loss, loss_fn, compute_grad_norm, compute_abs_mean
from tqdm import tqdm
import gc
from collections import deque

from rich.live import Live
from rich.table import Table
from rich.progress import Progress
from rich.console import Group

### Constants
shard_contrain = jax.lax.with_sharding_constraint
gn_threshold = None
am_threshold = None
static_mask = False


class Sharding:
    def __init__(self,shape) -> None:
        devices = np.array(jax.devices()).reshape(shape).transpose((1, 0))
        self.mesh = Mesh(devices, axis_names=('model', 'data'))

    def return_distr(self,x):
        return jax.device_put(x, NamedSharding(self.mesh ,self.get_spec(x)))

    def get_distribution(self,params):
        return tree_fn.apply_tree_fn(params,self.return_distr)
    
    def get_spec(self,x):
        if x.ndim == 1:
            return P('model')
        elif x.ndim == 2:
            return P(None, 'model')
        elif x.ndim == 3:
            return P(None, None, 'model')
        elif x.ndim == 0:
            return P()
        else:
            raise ValueError(f"The init weights contain a dim with {x.ndim} axis and it's still not recognised on which axis to shard")
    
    def get_struct(self,params):
        return tree_fn.apply_tree_fn(params,self.get_spec)
    
    def get_batch_train(self,params,opt_state):
        struct = self.get_struct(params)
        opt_struct = self.get_struct(opt_state)
        def BatchTrain(params, grad_fn, model_struct, x, mask, y, key, optimizer, opt_state):
            loss, grad = grad_fn(params, model_struct, [x,mask,y], key)

            synced_grad = jax.lax.pmean(grad, axis_name='data')

            updates, new_opt_state = optimizer.update(synced_grad, opt_state, params)
            new_params = optax.apply_updates(params, updates)

            return loss, new_params, new_opt_state
        
        return pjit(
            BatchTrain,
            in_shardings=(
                struct,
                P('data',None),
                P('data',None),
                P('data',None),
                None,
                opt_struct
            ),
            out_shardings=(None,struct, opt_struct),
            static_argnums=(1, 2, 7),
            donate_argnums=(0,8)
        )
    
    def get_batch_trainV2():
        def BatchTrain(params, grad_fn, model_struct, x, mask, y, key, optimizer, opt_state,chunks, grad_accum=1):

            micro_batch = x.shape[0] // grad_accum
            x = jax.lax.reshape(x, (grad_accum, micro_batch, x.shape[-1]))
            mask = jax.lax.reshape(mask, (grad_accum, micro_batch, x.shape[-1]))
            y = jax.lax.reshape(y, (grad_accum, micro_batch, x.shape[-1]))
            grad = jax.tree.map(jnp.zeros_like, params)
            
            def grad_micro_bt_low(carry,x):
                loss, grad = grad_fn(params, model_struct, x, key, chunks)
                return jax.tree_util.tree_map(lambda x, y: x + y, grad, carry), loss
            
            grad_all, loss = jax.lax.scan(grad_micro_bt_low, grad, (x, mask, y))
            loss = loss.mean()
            grad = jax.tree_util.tree_map(lambda x: x/grad_accum,grad_all)

            grad_norm, norm_per_layer = compute_grad_norm(grad)
            grad_abs, abs_per_layer = compute_abs_mean(grad)
            
            if gn_threshold is not None:
                grad = jax.tree_util.tree_map(
                    lambda g, n: jax.lax.cond(
                        n > gn_threshold,
                        lambda _: g * (gn_threshold / (n)),
                        lambda _: g,
                        operand=None
                    ),
                    grad,
                    norm_per_layer
                )

            if am_threshold is not None:
                if am_threshold == "auto":
                    grad = jax.tree_util.tree_map(
                        lambda g, n: jax.lax.cond(
                            n > grad_abs,
                            lambda _: g * (grad_abs / (n)),
                            lambda _: g,
                            operand=None
                        ),
                        grad,
                        abs_per_layer
                    )
                else:   
                    grad = jax.tree_util.tree_map(
                        lambda g, n: jax.lax.cond(
                            n > am_threshold,
                            lambda _: g * (am_threshold / (n)),
                            lambda _: g,
                            operand=None
                        ),
                        grad,
                        abs_per_layer
                    )

            updates, new_opt_state = optimizer.update(grad, opt_state, params)
            new_params = optax.apply_updates(params, updates)
            return loss, new_params, new_opt_state, [norm_per_layer, grad_norm], [abs_per_layer, grad_abs]
        
        return jax.jit(
            BatchTrain,
            static_argnums=(1, 2, 4, 7, 9, 10) if static_mask else (1, 2, 7, 9, 10),
            donate_argnums=(0,8)
        )

    def get_batch_trainV3():
        def BatchTrain(params, grad_fn, model_struct, x, mask, y, key, optimizer, opt_state, chunks,grad_accum=1):
            batch_size, seq_len = x.shape
            microbatch_size = batch_size // grad_accum

            triplet = jax.lax.concatenate([x[:, None, :], mask[:, None, :].astype(x.dtype), y[:, None, :]], dimension=1)
            reshaped = jax.lax.reshape(triplet, (grad_accum, microbatch_size, 3, seq_len))
            data = jax.lax.transpose(reshaped, (0, 2, 1, 3))
            data = shard_contrain(data,P(None, None,'data', None))   #(grad_accum_steps, 3, microbatch, seq_len)

            grad = jax.tree.map(jnp.zeros_like, params)

            def fw_pass(carry,x):
                loss, grad = grad_fn(params, model_struct, x, key, chunks)
                carry = jax.tree_util.tree_map(lambda x, y: x + y, grad, carry)
                return carry,loss
            
            grad, loss = jax.lax.scan(fw_pass,grad,data)
            grad = jax.tree_util.tree_map(lambda x: x/grad_accum,grad)
            updates, new_opt_state = optimizer.update(grad, opt_state, params)
            new_params = optax.apply_updates(params, updates)
            return loss.mean(), new_params, new_opt_state
        
        return jax.jit(
            BatchTrain,
            static_argnums=(1, 2, 7, 9),
            donate_argnums=(0,8)
        )

def train_batch(model, BatchTrain, x, mask, y, step, chunks, grad_accum):
    key = model.key_bruh
    loss, model.params, model.optimizer.state, [N_per_layer, grad_norm], [A_per_layer, abs_mean] = BatchTrain(model.params,model.grad_fn,model.model_struct,x,mask,y,key,model.optimizer.optimizer,model.optimizer.state, chunks, grad_accum)
    model.stats['grad_norm'] = jax.tree_util.tree_map(
        lambda avg, new: avg + (float(new) - avg) / step,
        model.stats['grad_norm'],
        N_per_layer
    )

    model.stats['abs_mean'] = jax.tree_util.tree_map(
        lambda avg, new: avg + (float(new) - avg) / step,
        model.stats['abs_mean'],
        A_per_layer
    )
    return loss, grad_norm, abs_mean

def train(model,x,mask,y,epochs,batch_size,optimizer,lr_data,val_x=None,val_mask=None,val_y=None,val_step=100,updates_in=1,avg_mem=25,state_path=None,mesh=(1,1),chunks=1, cp_after=None, grad_accum=1, chunked_training=False, total_steps=None):
    # The training function will be here soon
    pass