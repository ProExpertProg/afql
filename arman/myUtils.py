import pandas
import torch
import torch.nn as nn
from torch.nn import parameter

def endsInFilename(elt, valid_endings):
    for ending in valid_endings:
        if elt.endswith(ending):
            return True
    return False

def sparsity(model):
    # Return global model sparsity
    a, b = 0, 0
    for p in model.parameters():
        a += p.numel()
        b += (p == 0).sum()
    return b / a

def convertDfToCsv(df,csv_path):
    df.to_csv(csv_path)
    return

def get_model_size(model: nn.Module, data_width=32):
    """
    calculate the model size in bits
    :param data_width: #bits per element
    """
    num_elements = 0
    for param in model.parameters():
        num_elements += param.numel()
    return num_elements * data_width

Byte = 8
KiB = 1024 * Byte
MiB = 1024 * KiB
GiB = 1024 * MiB