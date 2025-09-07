from . .common_imports import *
from . ._errors import ModelNotFound
from . .independent import Tokenization

# IMP: This code is not tested because.... We don't have a model on this # But for some reason it works completely fine on not so working models :/ (Lmao i am keeping this comment here because it's funny XD)
class ReadyToUse():
    def __init__(self):
        self.tok = Tokenization()
        print("You are using incompatable code right now, Only KV caching inference supports the current models")
        self.model = None
        self.model_name = None
    
    def __call__(self,prompt,model = None,max_len=20):
        from . .main import load_hf as load_hf_low
        if model is None:
            if self.model is None:
                raise ModelNotFound("There is no model loaded for it to be used.... Enter a model To be loaded or skip it to use a preloaded model.")
        self.tok = Tokenization()
        if (self.model_name != model) or (model is None):
            self.model = load_hf_low(model)
            self.model_name = model
        return self.pred_low(prompt, max_len)

    def sample_next_token(self, logits, temperature=1.0):
        probs = np.exp(logits / temperature)
        probs /= np.sum(probs)
        return np.random.choice(len(probs), p=probs)

    def pred_low(self,prompt, max_length=50, temperature=1.0):
        # Tokenize the initial prompt
        initial_input_ids, initial_mask = self.tok.tokenize_([prompt])
        batch_size, initial_length = initial_input_ids.shape[0], initial_input_ids.shape[1]
        total_length = initial_length + max_length
        
        # Get the pad token ID from the tokenizer
        pad_token_id = 0
        
        # Pre-allocate input_ids and mask with static shapes
        padded_input_ids = np.full((batch_size, total_length), pad_token_id, dtype=initial_input_ids.dtype)
        padded_mask = np.zeros((batch_size, total_length), dtype=initial_mask.dtype)
        
        # Copy the initial prompt into the padded arrays
        padded_input_ids[:, :initial_length] = initial_input_ids
        padded_mask[:, :initial_length] = initial_mask
        
        for step in range(max_length):
            current_position = initial_length + step
            # Get logits for the next token from the current position
            logits = self.model.jax_call(padded_input_ids, padded_mask)[0, current_position - 1, :].astype(np.float32)
            next_token = self.sample_next_token(logits, temperature)
            
            # Update the padded arrays with the new token
            padded_input_ids[:, current_position] = next_token
            padded_mask[:, current_position] = 1
        
        # Decode the generated sequence, removing padding if necessary
        return self.tok.decode(padded_input_ids[0])

SetUpAPI = ReadyToUse()