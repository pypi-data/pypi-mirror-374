from . .common_imports import *
from . ._utils import tree_fn
from tqdm import tqdm
from . ._utils import loss_fn

def grad_check(model,x,mask,y,batch_size):
    num_devices = jax.device_count()
    grad_fn = jax.value_and_grad(loss_fn)
    print(f"Number of bad boies dectected: {num_devices} potatoes")
    loss, stats,v,e = [],None,[],[]
    batched = model.batch_it(x=x,mask=mask,y=y,batch_size=batch_size)
    batch_len = len(batched)
    with tqdm(total=batch_len, unit='batch') as pbar:
        for x,mask,y in batched.stream_it():
            key = model.key_bruh
            loss_temp,stats_temp,(v_,e_) = grad_check_low(
                model.params,
                grad_fn,
                model.model_struct,
                x,
                y,
                mask,
                key
            )
            loss.append(loss_temp)
            stats = stats_temp if stats is None else tree_fn.avg_trees(stats,stats_temp)
            v.append(v_)
            e.append(e_)
            pbar.set_postfix(
                loss = f"{sum(loss)/len(loss)}",
                vanishing = f"{sum(v)/len(v)}",
                exploding = f"{sum(e)/len(e)}"
            )
            pbar.update(1)
        
    return loss,stats,v,e


def grad_check_low(params,grad_fn,model_struct,x,y,mask,key):
    loss, grad = grad_fn(params, model_struct, [x,mask,y], key)
    all_grad_values = tree_fn.flatten_tree(grad)

    near_zero_count = jnp.sum(jnp.abs(all_grad_values) < 1e-6)
    total_count = all_grad_values.size
    zero_ratio = near_zero_count / total_count

    exploding_count = jnp.sum(jnp.abs(all_grad_values) > 1e2)
    exploding_ratio = exploding_count / total_count
    stats = tree_fn.apply_tree_fn(grad,stat_fn)
    return loss,stats,[zero_ratio,exploding_ratio]


grad_check_low = jax.jit(
    grad_check_low,
    static_argnums=(1, 2),
    donate_argnums=(0,3,4,5,6)
)

grad_check_low = jax.pmap(  
    grad_check_low,
    static_broadcasted_argnums=(1, 2),
    in_axes=(None, None, None, 0, 0, 0, None,None),
    axis_name="batch",
    out_axes=None
)


def stat_fn(array):
    mean = jnp.mean(array)
    std = jnp.std(array)
    max_val = jnp.max(array)
    min_val = jnp.min(array)
    median = jnp.median(array)
    abs_mean = jnp.mean(jnp.abs(array))

    near_zero_count = jnp.sum(jnp.abs(array) < 1e-6)
    total_count = array.size
    zero_ratio = near_zero_count / total_count

    exploding_count = jnp.sum(jnp.abs(array) > 1e2)
    exploding_ratio = exploding_count / total_count

    return{
        "mean":mean,
        "std":std,
        "max_val":max_val,
        "min_val":min_val,
        "median":median,
        "abs_mean":abs_mean,
        'zero_ratio':zero_ratio,
        'exploding_ratio':exploding_ratio
    }