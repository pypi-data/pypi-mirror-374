import inspect
import os
from jax import ensure_compile_time_eval

class IncorrectDtype(Exception):
    def __init__(self,message):
        super().__init__(message)

class ModelHpMismatch(Exception):
    def __init__(self,message):
        super().__init__(message)

class DebugError(Exception):
    def __init__(self,message):
        super().__init__(message)

class ModelNotFound(Exception):
    def __init__(self,message):
        super().__init__(message)

class Experiment(Exception):
    def __init__(self,message):
        super().__init__(message)

class UnusableModule(Exception):
    def __init__(self,message):
        super().__init__(message)

class ShapeMismatch(Exception):
    def __init__(self,message):
        function_info = get_function_info()
        message = (
            f"File: {function_info['file']}\n"
            f"Line: {function_info['line']}\n"
            f"Function: {function_info['function']}\n"
            f"{'═' * 60}\n"
            f"{message}"
        )
        super().__init__(message)
        
def get_function_info():
    frame = inspect.currentframe().f_back
    info = inspect.getframeinfo(frame)
    return {
        "file": os.path.abspath(info.filename),
        "line": info.lineno,
        "function": frame.f_code.co_name
    }

def shape_check(*check_items):
    """Get stuff in the format Var, ndim, shape, var_name \n you can use None if it's not to check but 0 and -1 is a must"""
    with ensure_compile_time_eval():
        check_items = [check_items]
        for item in list(check_items):
            for Var, ndim, shape, var_name in item:
                if ndim is not None:
                    if len(Var.shape) != ndim:
                        raise ShapeMismatch(f"The varaible called '{var_name}' is suppose to have a ndim of {ndim} but got a ndim of {len(Var.shape)}")
                
                if shape is not None:
                    for x, y in zip(Var.shape,shape):
                        if y is None:
                            pass
                        elif x != y:
                            raise ShapeMismatch(f"The variable called '{var_name}' is suppose to have a shape of {shape} but got a shape of {Var.shape}")

def shape_match(*args):
    with ensure_compile_time_eval():
        shapes = [x[0].shape for x in args]
        if len(set(shapes)) != 1:
            raise ShapeMismatch(f"There is a shape mismatch for variables who's name is {[x[1] for x in args]} and shapes are {[x[0].shape for x in args]}.")