from . .independent import Tokenization
from .data_low import Load
from .data_low import Load_dataset, save_ds_np, data_mixer_low
import json


### Constant
tok = Tokenization()

def process(name,file,toke_len,start,stop=None,num_cores=2,save=False):
    data = Load(name,file,start,stop)
    tok_data=tok.tokenize_max_util(data,num_cores,toke_len)
    if save:
        save_ds_np(tok_data,"saved_ds.npy")
    return tok_data


def process_local(path,toke_len,num_cores=2,*args,**kwargs):  # not tested but it works ig
    data = Load_dataset.load_json(path)
    return tok.tokenize_max_util(data,num_cores,toke_len)

def data_mixer(*args,**kwargs):
    return data_mixer_low(*args,**kwargs)

"""
Stuff to keep track of:
Name:
num_params:
loss:
val loss:
lr:
tot_time:
tot_tokens:
And what? 
"""

class ProgressTracker:
    def add(path,losses,val_loss,lr,time,tokens,**kwargs):
        with open(path, 'r') as f:
            data = json.load(f)
        data['loss'].append(losses)
        data['val_loss'].append(val_loss)
        data['lr'] = lr,
        data['total time'] += time
        data['total tokens'] += tokens
        for attr, value in kwargs.items():
            if isinstance(value,list):
                data[attr].append(value)
            else:
                data[attr].extend(value)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def create(path,model_name,num_params,**kwargs):
        data = {'name':model_name,
                'num_params':num_params,
                'total tokens': 0,
                'total time':0,
                "loss":[],
                "val_loss":[],
                'stats':["name","num_params","total tokens","total time",'loss',"val_loss"]}
        
        if kwargs:
            print("All the additionally added attrs for the model stats")
            for attr, value in kwargs.items():
                data[attr] = value
                print(f"{attr}: {value}")
                print("---")
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def show(path,attr):
        with open(path, 'r') as f:
            data = json.load(f)
            return data[attr]