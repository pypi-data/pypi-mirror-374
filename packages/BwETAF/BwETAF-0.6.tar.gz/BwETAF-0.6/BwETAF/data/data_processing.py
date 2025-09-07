from . .common_imports import *
from tqdm import tqdm

def get_prob_tokens(labels: np.ndarray, batch_size: int, vocab_size: int = 50258, to_return:list=[None, 10]):
    freqs = np.zeros(vocab_size, dtype=np.int64)
    total_tokens = 0

    for i in tqdm(range(0, labels.shape[0], batch_size), desc="Processing batches"):
        batch = labels[i:i+batch_size]
        unique, counts = np.unique(batch, return_counts=True)
        freqs[unique] += counts
        total_tokens += batch.size
    sorted_indices = np.argsort(freqs)[::-1]
    
    return sorted_indices[to_return[0]:to_return[1]]

def mask_logits(arr: np.ndarray, mask_values: list):
    mask = np.isin(arr, np.array(mask_values))
    return np.where(mask, -1, arr)