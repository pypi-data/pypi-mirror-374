import numpy as np
from . .model.model import ModelManager
from typing import Tuple
from . .common_imports import *
from tqdm import tqdm

def sort_data(model: ModelManager, data: Tuple[np.ndarray, np.ndarray] | Tuple[np.ndarray, np.ndarray, np.ndarray], batch_size: int, logits_chunking: int=1):
    data_batched = model.batch_it(x=data[0], mask=data[1], y=data[2], batch_size=batch_size)
    num_devices = jax.device_count()
    print(f"Number of bad boies dectected: {num_devices} potatoes")
    all_points = []
    with tqdm(total=len(data_batched), desc="Sorting", unit='batch') as pbar:
        for x, mask, y in data_batched.stream_it():
            key = model.key_bruh
            points = loss_fn(model.params, model.model_struct, [x, mask, y], key, logits_chunking)
            all_points.append(points.flatten())
            pbar.update(1)
        
        all_points = jnp.concatenate(all_points)
        return jnp.argsort(all_points), all_points

def combined_sorting(data, data_set, start=0, end=-1):
    """Input: 
    - data -> This is a list containing tuples like [('name', percent),('name2, percent)]
    - data_set [np.ndarray] -> The labels in the shape (total number of sentence, sequence length), this at the moment supports format compatable with the model and only works with labels and not masks
    - start -> If you want to trim the dataset and exclude the first few, Default set to 0
    - end -> Same as start but how much to trin, Default set to -1
    
    Returns:
    - np.array with shape (total left after trimming, sequence length)"""
    overall_ranking = None
    for name, percent in data:
        per_data = np.load(name)
        normalized_per_data = ((per_data - per_data.mean()) / per_data.std())*percent
        if overall_ranking is None:
            overall_ranking = normalized_per_data
        else:
            overall_ranking = overall_ranking + normalized_per_data
    
    return data_set[np.argsort(overall_ranking)][start:end]

def reshape_mask(data: np.ndarray, seq_len: int):
    x = data.reshape((-1,seq_len))
    return x, np.ones(x.shape)

@partial(jax.pmap,
         in_axes=(None, None, 0, None, None),
         static_broadcasted_argnums=(1,4)
         )
@partial(jax.jit,
        static_argnums=(1,4)
        )
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
    assert b % chunks == 0, "Batch size must be divisible by chunks!"
    block_op = jax.lax.reshape(block_op,(chunks,b//chunks,s,d))
    b,s = f_targets.shape
    f_targets = jax.lax.reshape(f_targets,(chunks,b//chunks,s))

    def chunk_fn(_, x):
        c_block_op, targets = x
        logits = model.apply(params,c_block_op,method=model.last_layer_fn)
        logits = logits.astype(jnp.float32)
        shifted_logits = logits[:, :-1, :]  # (B, T-1, C)
        shifted_targets = targets[:, 1:]    # (B, T-1)
        debug_ = optax.softmax_cross_entropy_with_integer_labels(shifted_logits, shifted_targets).mean(axis=-1)
        return None, debug_
    return jax.lax.scan(chunk_fn,None,(block_op, f_targets))[1].flatten()