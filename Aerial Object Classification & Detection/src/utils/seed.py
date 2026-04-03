import os
import random
import numpy as np


def set_seed(seed: int = 42) -> None:
    """
    Set seed for reproducibility.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)