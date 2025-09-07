from ._errors import *
from .common_imports import *

### Constants that can be changed from outside
gn_threshold = None
am_threshold = None
static_mask = False


def time_it(fn, *args,**kwargs):
    t0 = time.time()
    out = fn(*args,**kwargs)
    t1 = time.time()
    return out, t1 - t0

def compute_grad_norm(grads):
    squared_norms = jax.tree_util.tree_map(lambda g: jnp.sum(jnp.square(g)), grads)

    norms_flat, _ = jax.tree_util.tree_flatten(squared_norms)
    total_norm = jnp.sqrt(jnp.sum(jnp.array(norms_flat)))

    return total_norm, squared_norms

def compute_abs_mean(grads):
    squared_mean = jax.tree_util.tree_map(lambda g: jnp.mean(jnp.abs(g)), grads)

    mean_flat, _ = jax.tree_util.tree_flatten(squared_mean)

    return jnp.array(mean_flat).mean(), squared_mean


def loss_fn(params, model, batch, rng,chunks=1):
    inputs, mask, f_targets = batch

    block_op = model.apply(
        params,
        inputs,
        mask,
        training=True,
        rngs={'dropout': rng},
        method=model.prim_run
    )
    b,s,d = block_op.shape
    assert s % chunks == 0, "Seq len must be divisible by chunks!"
    block_op = jax.lax.reshape(block_op,(chunks,b,s//chunks,d))
    b,s = f_targets.shape
    f_targets = jax.lax.reshape(f_targets,(chunks,b,s//chunks))
    @jax.remat
    def chunk_fn(_, x):
        c_block_op, targets = x
        logits = model.apply(params,c_block_op,method=model.last_layer_fn)
        logits = logits.astype(jnp.float32)
        shifted_logits = logits[:, :-1, :]  # (B, T-1, C)
        shifted_targets = targets[:, 1:]    # (B, T-1)
        mask = (shifted_targets != -1).astype(jnp.uint16)
        results = optax.softmax_cross_entropy_with_integer_labels(shifted_logits, shifted_targets) * mask
        return None, results.sum()/jnp.maximum(mask.sum(), 1.0)
    return jax.lax.scan(chunk_fn,None,(block_op, f_targets))[1].mean()

def grad_trans(grad):
    return grad


@partial(jax.pmap,
        in_axes=(None,None,None,0,0,0,None,None),
        static_broadcasted_argnums=(1,2,7),
        axis_name='batch'
        )
@partial(jax.jit,
        static_argnums=(1,2,7)
        )
def val_loss(params, loss_fn, model_struct, x,mask,y, key,chunks):
    return loss_fn(params, model_struct, [x,mask,y], key,chunks)


# Main training step

def BatchTrain_retired(params, grad_fn, model_struct, x, mask, y, key, optimizer, opt_state):
    loss, grad = grad_fn(params, model_struct, [x,mask,y], key)
    grad = jax.lax.pmean(grad, axis_name="batch")
    updates, opt_state = optimizer.update(grad, opt_state,params=params)
    params = optax.apply_updates(params, updates)
    return jax.lax.pmean(loss, axis_name="batch"), params, opt_state


@partial(jax.pmap,
        static_broadcasted_argnums=(1, 2, 7, 9, 10),
        in_axes=(None, None, None, 0, 0, 0, None, None, None, None, None),
        axis_name="batch",
        out_axes=None
        )
@partial(jax.jit,
        static_argnums=(1, 2, 4, 7, 9, 10) if static_mask else (1, 2, 7, 9, 10),
        donate_argnums=(0,3,4,5,6,8)
        )
def BatchTrain(params, grad_fn, model_struct, x, mask, y, key, optimizer, opt_state, chunks, grad_accum=1):
    #Step function will be here soon...
    pass

#Some sharding stuff

def get_P_representation(num):         # This function is working but not in use anymore
    args = [None] * (num - 1) + ['model']
    return P(*args)

def is_inside_mesh():
    try:
        mesh = jax.sharding.get_current_mesh()
        return mesh is not None
    except Exception:
        return False

def lax_matmul(V1,V2,cr1,cr2,b,sharding_specs=None):
    if is_inside_mesh() and sharding_specs is not None:
        V1 = jax.lax.with_sharding_constraint(V1, sharding_specs[0])
        V2 = jax.lax.with_sharding_constraint(V2, sharding_specs[1])

    dimension_numbers = (
            (cr1, cr2),
            (b, b)
        )
    try:
        return jax.lax.dot_general(V1, V2, dimension_numbers)
    except TypeError as e:
        raise ShapeMismatch(f"Tried doing matmul with 2 incompatible array which had shapes \n Shape:{V1.shape}, added_dim:{cr1}\nShape:{V2.shape}, added_dim:{cr2}\nBatch_dim:{b}")

# Pytree functions
class tree_fn():
    def get_first(pytree):
        return jax.tree_util.tree_map(lambda x: x[0], pytree)

    def convert_tree(dtype,pytree):
        return jax.tree_util.tree_map(lambda x: x.astype(dtype),pytree)

    def pytree_dtype(pytree):
        return jax.tree_util.tree_leaves(pytree)[0].dtype
    
    def shapes(pytree):
        return jax.tree_util.tree_map(lambda x: x.shape,pytree)
    
    def check_for_nan(pytree):
        def has_nan(x):
            return jnp.isnan(x).any()

        nans = jax.tree_util.tree_map(has_nan, pytree)
        flat_nans = jax.tree_util.tree_flatten(nans)[0]
        return any(flat_nans)   

    def flatten_tree(grads):
        flat_grads = jax.tree_util.tree_leaves(grads)
        all_values = [g.ravel() for g in flat_grads if g is not None]
        return jnp.concatenate(all_values)
    
    def apply_tree_fn(tree,func):
        return jax.tree_util.tree_map(lambda x:func(x),tree)
    
    def avg_trees(tree1, tree2):
        return jax.tree_util.tree_map(lambda a, b: (a + b) / 2, tree1, tree2)
    

class KeyManager:
    def __init__(self, seed=42):
        self.key = jax.random.PRNGKey(seed)

    def next_key(self):
        self.key, subkey = jax.random.split(self.key)
        return subkey

key = KeyManager()             # Constant here too

def get_hlo(func,file_name="result.hlo",*args,**kwargs):
    lowered = jax.jit(func).lower(*args,**kwargs)

    compiled = lowered.compile()

    with open(file_name ,"w") as f:
        f.write(compiled.as_text())
    

class TrainRailGuard:
    def __init__(self,func_cp,least_drop_cp=2.5,critical_stop=3) -> None:
        self.tick = 0
        self.prev_loss = None
        self.least_drop_cp = least_drop_cp
        self.func_cp = func_cp
        self.critical_stop = critical_stop
        self.x = "CONFIRM"
        self.guard = True
        self.cp_num = 0
    
    def check_loss(self,loss):
        if self.prev_loss is None and self.guard:
            pass
        else:
            diff = abs(self.prev_loss - loss)
            if diff > self.least_drop_cp:
                print("Checkpointing because major loss functuation decteted")
                self.func_cp(f"safe_checkpoint{self.cp_num}")
                self.cp_num = self.cp_num + 1
            if diff > self.critical_stop:
                x = input("Critical loss drop dictected, Waiting for user confimation to continue(Continue): ")
                if x == "Continue":
                    self.guard = False

        self.prev_loss = loss

    def lr_check(self,lr,lrf,min_lr=5e-6):
        if lr < lrf:
            print("The final lr is greater! Hope you are in warmup")
        print(f"the learning rate drop is {lr-lrf}")
        if (lr < min_lr) or (lrf < min_lr):
            input("Lr is too low for the model to learn anything... Waiting for user command to continue: ")
            


def get_kv(struct):
    return flax.traverse_util.flatten_dict(struct, sep='/')