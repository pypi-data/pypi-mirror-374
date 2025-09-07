import flax.serialization
from .common_imports import *
from huggingface_hub import hf_hub_download, create_repo, upload_file, login
from .independent import debug_state
from ._utils import tree_fn
from .model.model import *
import gc


@debug_state.trace_func
def load_model(path,dtype= None):
    with open(os.path.join(path, "understanding_good_stuff.json"), "r") as f:
        data = json.load(f)
    
    data['dtype'], data['possible_opt_path'] = dtype, path
    model = ModelManager( **data)
    with open(os.path.join(path, "good_stuff.pkl"), "rb") as f:
        model.params = tree_fn.convert_tree(dtype,flax.serialization.from_bytes(model.params, f.read()))
    gc.collect()
    return model

@debug_state.trace_func
def load_hf(path,dtype= None):
    model_repo = path
    filenames = ["understanding_good_stuff.json","good_stuff.pkl","make_stuff_better.pkl","stats.json","tokenizer/yap.json","tokenizer/understanding_yap.json"]
    for i in filenames:
        try:
            print(hf_hub_download(repo_id=model_repo, filename=i,local_dir="Loaded_model"))
        except:
            print(f"No {i} found")
    gc.collect()
    return load_model("Loaded_model",dtype)

@debug_state.trace_func
def push_model(repo_name, folder_path):
    files_to_upload = ["good_stuff.pkl", "understanding_good_stuff.json","make_stuff_better.pkl","stats.json","tokenizer/yap.json","tokenizer/understanding_yap.json"]
    
    create_repo(repo_name, exist_ok=True)  # Create repo if it doesn’t exist

    for file_name in files_to_upload:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):  # Only upload if the file exists
            upload_file(
                path_or_fileobj=file_path,
                path_in_repo=file_name,  # Save with the same filename
                repo_id=repo_name,
                repo_type="model",
            )
    print(f"Uploaded {files_to_upload} to {repo_name}")