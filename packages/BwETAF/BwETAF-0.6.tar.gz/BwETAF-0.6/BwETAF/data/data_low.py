import json
import numpy as np
from huggingface_hub import hf_hub_download, upload_file
from . .common_imports import *

def save_ds_np(array,path="ds.npy"):
    np.save(path,array)

def load_ds_np(path):
    return np.load(path)

class Load_dataset():
    def load_txt(path,encode='utf-8'):
        with open(path, encoding=encode,mode='r') as file:
            return file.read()
    
    def load_json(path):
        with open(path,'r') as file:
            data = json.load(file)
        if isinstance(data,list):
            return data
        if isinstance(data,dict):
            return list(json.load(file).Values())
    
    def load_hf_formated(name,file):
        from datasets import load_dataset
        dataset = load_dataset(name, data_files=file)
        train_data_dict = dataset['train'].to_dict()["answer"]
        return train_data_dict

def Load(name,file,start=0,end=None):
    data = Load_dataset.load_hf_formated(name,file)
    if end is not None:
        return data[start:end]
    else:
        return data[start:]


def get_data(repo_id="WICKED4950/Raw-GPT-traindata", file="saved_ds.npy"):
    print("Plesae note that this is not a correctly working function")
    print(hf_hub_download(repo_id=repo_id, filename=file,local_dir="ds"))

def put_data(repo_id="WICKED4950/Raw-GPT-traindata", file="saved_ds.npy"):
    upload_file(
        path_or_fileobj=file,
        path_in_repo=file,  # Save with the same filename
        repo_id=repo_id,
        repo_type="dataset",
    )

def data_mixer_low(data:list, total_tokens:int, seq_len: int, dtype=np.uint16, seed=42,last=False):
    collected_data = []
    for name, percent in data:
        needed_sent = int((total_tokens * percent) / seq_len)
        print("Needed sent",needed_sent)
        if last:
            taken_before_reshape = np.load(name, mmap_mode='r').reshape((-1,seq_len)).astype(dtype)[-needed_sent:]
        else:
            taken_before_reshape = np.load(name, mmap_mode='r').reshape((-1,seq_len)).astype(dtype)[:needed_sent]
        print("The sentence is gonna be",taken_before_reshape.shape[0]*taken_before_reshape.shape[1])
        collected_data.append(taken_before_reshape)
        del taken_before_reshape, needed_sent
    
    main_ds = np.concatenate(collected_data, axis=0)
    np.random.seed(seed)
    np.random.shuffle(main_ds)
    return (main_ds, jnp.ones(main_ds.shape, dtype=dtype))


def make_mask_low(data, eos_token: int = 0):
    arr = jnp.asarray(data)
    B, L = arr.shape

    eos_pos = jnp.where(arr == eos_token, jnp.arange(L), -1)  # (B, L)
    last_eos = jnp.maximum.accumulate(eos_pos, axis=1)        # (B, L)

    pad = jnp.full((B, 1), -1, dtype=last_eos.dtype)
    last_eos_prev = jnp.concatenate([pad, last_eos[:, :-1]], axis=1)  # (B, L)
    start = last_eos_prev + 1

    i = jnp.arange(L)                     # (L,)
    t = jnp.arange(L)                     # (L,)

    # Broadcasted comparison
    mask = (i[None, None, :] >= start[:, :, None]) & \
           (i[None, None, :] <= t[None, :, None])   # (B, L, L)

    return mask[:, None, :]