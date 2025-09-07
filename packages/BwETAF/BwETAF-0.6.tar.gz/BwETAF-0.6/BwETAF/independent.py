from concurrent.futures import ProcessPoolExecutor
from._errors import *
from ._utils import *
from .common_imports import *
from ._utils import is_inside_mesh
from jax.tree_util import tree_map
import gc


### Some constants
shard_contrain = jax.lax.with_sharding_constraint



def encode(arg):
    text, enc = arg
    tokens = enc.encode(text, allowed_special={'<|endoftext|>'})
    return tokens

def encode_and_pad(args):
    text, enc, max_length, pad_token = args
    tokens = enc.encode(text, allowed_special={'<|endoftext|>'})[:max_length]
    padded = np.full(max_length, pad_token, dtype=np.int32)
    mask = np.zeros(max_length, dtype=np.int32)
    padded[:len(tokens)] = tokens
    mask[:len(tokens)] = 1  # Mark real tokens as 1
    return padded, mask

def cast_moments(opt_state, dtype):
    if dtype is None:
        return opt_state
    else:
        def cast_fn(x):
            # Only cast float32 arrays, skip ints and other non-float stuff
            if isinstance(x, jnp.ndarray) and x.dtype == jnp.float32:
                return x.astype(dtype)
            return x
        return tree_map(cast_fn, opt_state)

class Debugger():
    def __init__(self,debug = False,path=None) -> None:
        self.debug = debug
        self.path = path
        if path is not None:
            self.logfile = open(path, "a")
    
    def turn_debugger_on(self):
        self.debug = True
        self.logfile = open(self.path, "a")

    def logger(self,message,state="DEBUG"):
        if self.debug:
            if self.path is None:
                print(f"[{state}] {message}")
            else:
                self.logfile.write(f"[{state}] {message}\n")
                self.logfile.flush()
    
    def Alert(self,message):
        print(f"[WARNING] {message}")
        self.logger(message,state="WARNING")

    def trace_func(self,func):
        def wrapper(*args, **kwargs):
            self.logger(f"Calling {func.__name__} with args: {[type(i) for i in args]}, kwargs: {[type(i) for i in kwargs]} Shapes: {[getattr(i, 'shape', 'uk') for i in args]}",state="FUNC_CALL")
            start_time = time.time()
            try:
                out = func(*args, **kwargs)
            except Exception as e:
                self.logger(f"{func.__name__} Exception:{e}",state="ERROR")
                self.logger(traceback.format_exc(), state="TRACEBACK")
                raise
            name = f"{args[0].__class__.__name__}.__init__" if func.__name__ == "__init__" else func.__name__
            self.logger(f"{name} returned: {type(out)} with shape/info: {getattr(out, 'shape', 'uk')}, {getattr(out, 'dtype', 'uk')}, Time taken:{time.time()-start_time}s",state="FUNC_RETURN")
            return out
        return wrapper

debug_state = Debugger()


class Tokenization():
    @debug_state.trace_func
    def __init__(self,vocab="gpt2") -> None:
        import tiktoken
        print("BwETAF WARNING: You are trying to use the gpt2 tokenizer which is discontinued for the new models")
        self.stuff = tiktoken
        self.vocab = vocab
        self.enc = tiktoken.get_encoding(self.vocab)
        self.pad_token = self.eos_token = 50256

    @debug_state.trace_func
    def tokenize(self,batch:list, workers:int, max_length:int):
        self.enc = self.stuff.get_encoding(self.vocab)
        enc = self.enc
        
        args = [(text, enc, max_length, self.pad_token) for text in batch]
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(encode_and_pad, args))
        
        encoded_batch, mask = zip(*results)  # Split tokens and masks
        encoded_batch = np.array(encoded_batch)
        mask = np.array(mask)
        
        return encoded_batch, mask, np.where(mask == 0, -1, encoded_batch)

    @debug_state.trace_func
    def tokenize_max_util(self,data,workers,max_length):
        self.enc = self.stuff.get_encoding(self.vocab)
        enc = self.enc
        
        
        args = [(text, enc) for text in data]
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(encode, args))
        
        gc.collect()
        chain = []
        take = chain.append
        for i in results:
            if len(i) == 0:
                continue
            take(np.array(i))
            if chain[-1][-1] != self.eos_token:
                take(np.array([self.eos_token]))

        chain = np.array(np.concatenate(chain,axis=0))
        chain = chain[:chain.shape[0] - (chain.shape[0] % max_length)]
        content = chain.reshape(-1, max_length)
        del chain
        mask = np.ones(content.shape, dtype=np.uint16)
        return content, mask


    @debug_state.trace_func
    def tokenize_(self, batch: list):
        self.enc = self.stuff.get_encoding(self.vocab)
        enc = self.enc

        encoded_batch = []
        mask = []

        for text in batch:
            tokens = enc.encode(text, allowed_special={'<|endoftext|>'})
            encoded_batch.append(np.array(tokens, dtype=np.int32))
            mask.append(np.ones(len(tokens), dtype=np.int32))  # Mask matches token length
        
        return jnp.array(encoded_batch), jnp.array(mask)
    
    @debug_state.trace_func
    def decode(self,tokens):
        return self.enc.decode(tokens)
    
class Flax_ds():
    @debug_state.trace_func
    def __init__(self,x_eq_y:bool) -> None:
        self.x_eq_y = x_eq_y
        self.x = None
        self.mask = None
        self.y = None
        self.batch = None
    
    @debug_state.trace_func
    def load_data(self,x,mask,y):
        self.x = np.array(x, dtype=np.uint16)
        self.mask = np.array(mask, dtype=np.bool_)
        if not self.x_eq_y:
            self.y = np.array(y)
    
    @debug_state.trace_func
    def batch_it_(self,batch_size):
        if not self.x_eq_y:
            self.seq_len = self.x.shape[1]
            
            n_batches = len(self.x) // batch_size
            num_devices = jax.device_count()
            
            self.x_batch = [self.x[i * batch_size:(i + 1) * batch_size] for i in range(n_batches)]
            self.mask_batch = [self.mask[i * batch_size:(i + 1) * batch_size] for i in range(n_batches)]
            self.y_batch = [self.y[i * batch_size:(i + 1) * batch_size] for i in range(n_batches)]
            
            
            self.batch = [[i.reshape(num_devices,-1, self.seq_len), j.reshape(num_devices, batch_size // num_devices, *j.shape[1:]), k.reshape(num_devices,-1, self.seq_len)] for i, j, k in zip(self.x_batch, self.mask_batch, self.y_batch)]

            del self.x, self.mask, self.y
            return self.batch
        
        else:
            self.seq_len = self.x.shape[1]
            
            n_batches = len(self.x) // batch_size
            num_devices = jax.device_count()
            
            self.x_batch = [self.x[i * batch_size:(i + 1) * batch_size] for i in range(n_batches)]
            self.mask_batch = [self.mask[i * batch_size:(i + 1) * batch_size] for i in range(n_batches)]
            
            
            self.batch = [[i.reshape(num_devices,-1, self.seq_len), j.reshape(num_devices, batch_size // num_devices, *j.shape[1:])] for i, j in zip(self.x_batch, self.mask_batch)]

            del self.x, self.mask
            return self.batch
        
    
    def __len__(self):
        return len(self.batch)

    def stream_it(self):
        if self.batch == None:
            IncorrectDtype("Bruh... You forgot to run '.batch_it' before trying to stream it.... T~T")
        if self.x_eq_y:
            for i in self.batch:
                x = jnp.array(i[0])
                yield x,jnp.array(i[1]),x
        else:
            for i in self.batch:
                yield jnp.array(i[0]),jnp.array(i[1]),jnp.array(i[2])
        
    def stream_it_dir(self):
        if not is_inside_mesh:
            raise ValueError("This function is suppose to work only within a mesh")
        if not self.x_eq_y:
            self.batch = [[i.reshape(-1, self.seq_len), j.reshape(-1, self.seq_len), k.reshape(-1, self.seq_len)] for i, j, k in zip(self.x_batch, self.mask_batch, self.y_batch)]
            for i in self.batch:
                yield shard_contrain(i[0],P('data',None)).astype(jnp.uint16), shard_contrain(i[1],P('data',None)), shard_contrain(i[2],P('data',None)).astype(jnp.uint16)
        
        else:
            self.batch = [[i.reshape(-1, self.seq_len), j.reshape(-1, self.seq_len)] for i, j in zip(self.x_batch, self.mask_batch)]
            for i in self.batch:
                x = shard_contrain(i[0],P('data',None)).astype(jnp.uint16)
                yield x, shard_contrain(i[1],P('data',None)), x
    
    @property
    def gimme_the_data(self):
        return self.batch
    
def create_lr_schedule(peaklr, warmup_percent, total_steps,training_decay="linear" ,min_value=0, min_warmup_value=0,**kwargs):
    print("Unrec lr schedule args")
    print(kwargs)
    warmup_steps = int(warmup_percent*total_steps)
    warmup_fn = optax.linear_schedule(
            init_value=min_warmup_value,
            end_value=peaklr,
            transition_steps=warmup_steps
        )
    if training_decay == "linear":
        train_decay = optax.linear_schedule(
            init_value=peaklr,
            end_value=min_value,
            transition_steps=(total_steps - warmup_steps)
        )
    elif training_decay == "cosine":
        train_decay = optax.cosine_decay_schedule(
            init_value=peaklr,
            decay_steps=(total_steps - warmup_steps),
            alpha=min_value / peaklr
        )
    else:
        raise AttributeError(f"There is no decay type called {training_decay}")

    schedule = optax.join_schedules(
        schedules=[warmup_fn, train_decay],
        boundaries=[warmup_steps]
    )

    return schedule


# All the stuff for data for schedulers
"""
peaklr: int (5e-5 etc)
warmup_percent: 0 to 1 (0.10)
total_steps: uuh int ig
min_value: ig another lr but default is set to 0
"""

"""class Optimizer():
    @debug_state.trace_func
    def __init__(self,optimizer,lr,lrf,batches,epochs,params,dtype):
        decay_rate = (lrf / lr) ** (1 / (batches * epochs))
        self.lr_schedule = optax.exponential_decay(
            init_value=lr,
            transition_steps=1,
            decay_rate=decay_rate,
            staircase=False  # Smooth decay
        )
        self.optimizer = optimizer(self.lr_schedule)
        self.state = self.optimizer.init(params)
        if dtype is not None:
            print("The optimizer is in:",tree_fn.pytree_dtype(self.state))"""


class Optimizer():
    @debug_state.trace_func
    def __init__(self,optimizer,params,data):
        optimzer_init_data = {
            "weight_decay": data.get('weight_decay',0.0),
            "b1": data.get('b1',0.9),
            'b2':data.get('b2',0.99),
            'eps': data.get('eps',1e-8)
        }
        self.lr_schedule = create_lr_schedule(**data)
        self.optimizer = optimizer(self.lr_schedule, **optimzer_init_data)
        self.state = cast_moments(self.optimizer.init(params), data.get('opt_dtype', None))
    
    @debug_state.trace_func
    def load(self,path,dtype=None):
        try:
            with open(os.path.join(path, "make_stuff_better.pkl"), "rb") as f:
                self.state = flax.serialization.from_bytes(self.state, f.read())
                if dtype is not None:
                    print(f"WARNING! The optimzers is getting converted into {dtype} and that is gonna mess with the count var in the it's state")
                    self.state = tree_fn.convert_tree(dtype,self.state) 
                print("Using loaded optimizer states")
        except:
            print("No optimizers states found")

    @debug_state.trace_func
    def save(self,path):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "make_stuff_better.pkl"), "wb") as f:
            f.write(flax.serialization.to_bytes(self.state))