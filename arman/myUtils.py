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