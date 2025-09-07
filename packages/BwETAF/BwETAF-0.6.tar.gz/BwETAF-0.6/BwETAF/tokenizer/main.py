from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders, normalizers
from tokenizers.normalizers import NFD, StripAccents
from concurrent.futures import ProcessPoolExecutor
from tokenizers import AddedToken
import numpy as np
from math import ceil
import json
import os

tokenizer_global = None

def create(name,
           use_nfd = True,
           use_strip = True,
           unk_token = "<|UK|>",
           eos_token = "<|EOS|>",
           ):
    tokenizer = Tokenizer(models.BPE(unk_token=unk_token))
    tokenizer.normalizer = normalizers.Sequence([n() for n, use in [(NFD, use_nfd), (StripAccents, use_strip)] if use])
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    tokenizer.eos_token = eos_token
    tokenizer.unk_token = unk_token
    return tok(tokenizer, name)

def load(path):
    tokenizer = Tokenizer.from_file(os.path.join(path, "tokenizer/yap.json"))
    with open(os.path.join(path, "tokenizer/understanding_yap.json"), "r") as f:
        trainer_config = json.load(f)
    
    tok_temp = tok(tokenizer, trainer_config['name'])
    tok_temp.trainer_config = trainer_config
    tok_temp.tokenizer.eos_token = trainer_config['eos_token']
    tok_temp.tokenizer.unk_token = trainer_config['uk_token']
    return tok_temp

class tok:
    def __init__(self,tok_obj, name) -> None:
        self.tokenizer = tok_obj
        self.name = name
    
    def train(self,
              data,
              vocab_size,
              min_frequency: int = 6,
              special_tokens: list = [],
              ):
        trainer = trainers.BpeTrainer(
            vocab_size=vocab_size, 
            min_frequency=min_frequency,  # Only include tokens that appear at least twice
            special_tokens=special_tokens,  # Common special tokens
            initial_alphabet=pre_tokenizers.ByteLevel.alphabet()  # Start with byte-level alphabet
        )

        self.tokenizer.train_from_iterator(data, trainer=trainer)

        self.trainer_config = {
            'name': self.name,
            'vocab_size': self.tokenizer.get_vocab_size(),
            'special_tokens': special_tokens,
            'eos_token': self.tokenizer.eos_token,
            'uk_token': self.tokenizer.unk_token
        }

    def save(self, path):
        os.makedirs(path,exist_ok=True)
        os.makedirs(os.path.join(path, "tokenizer"),exist_ok=True)
        self.tokenizer.save(os.path.join(path, "tokenizer/yap.json"))
        with open(os.path.join(path, "tokenizer/understanding_yap.json"), "w") as f:
            json.dump(self.trainer_config, f, indent=2)
    
    def encode(self,text):
        """Takes in string and gives off list of ints"""
        return self.tokenizer.encode(text).ids
    
    def decode(self, ids):
        return self.tokenizer.decode(ids, skip_special_tokens=False)
    
    @staticmethod
    def encode_static(text):
        return tokenizer_global.encode_batch(text, add_special_tokens=tokenizer_global.add_special_tokens)
    
    def tokenize_max_util(self,data: list, workers:int = 1, max_length:int| None = None, add_special_tokens: bool = True):
        global tokenizer_global
        self.tokenizer.add_special_tokens = add_special_tokens
        tokenizer_global = self.tokenizer
        args = [text+self.tokenizer.eos_token for text in data]
        chunk_size = ceil(len(args)/workers)
        chunks = [args[chunk_size*i:chunk_size*(i+1)] for i in range(workers)]
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(tok.encode_static, chunks))
        
        results = [e.ids for chunk in results for e in chunk]
        chain = np.concatenate([np.array(i) for i in results if len(i) > 0], axis=0)
        if max_length is None:
            return chain
        else:
            chain = chain[:chain.shape[0] - (chain.shape[0] % max_length)]
            return chain.reshape(-1, max_length)