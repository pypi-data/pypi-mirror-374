import jax
import flax
import optax
import jax.numpy as jnp
import numpy as np
import time
from functools import partial
from jax.sharding import PartitionSpec as P
import traceback
import os
import flax.linen as nn
import json
import sys