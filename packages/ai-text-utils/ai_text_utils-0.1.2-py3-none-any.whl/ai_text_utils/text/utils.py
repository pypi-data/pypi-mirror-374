import tiktoken
import torch
import numpy as np
import requests
from urllib.parse import urlparse
import re
from .datasets import GenTextDataset
from torch.utils.data import DataLoader

class Tokenizer:
    def __init__(self, encoding='gpt-4'):
        self.encoder = tiktoken.encoding_for_model('gpt-4')
        
    def encode(self, txt):
        return self.encoder.encode(txt)

    def decode(self, tokens):
        if isinstance(tokens, torch.Tensor):
            tokens = tokens.trunc().int().cpu().numpy().tolist()
        elif isinstance(tokens, np.ndarray):
            tokens = tokens.astype(np.int64).tolist()
        elif isinstance(tokens, (int, float)):
            tokens = [int(tokens)]
        elif not isinstance(tokens, list):
            raise TypeError(f'Unsupported type : {type(tokens)}') 

        return self.encoder.decode(tokens)

    def vocab_size(self):
        return self.encoder.n_vocab

def gen_txt(model,initial_txt=None,device=None,tokenizer=None, seq_len=20, max_tokens=100):
    if initial_txt is None or model is None:
        print('inital txt or model is null')
        return

    tokens = tokenizer.encode(initial_txt)
    tokens = np.array(tokens)
    tokens = tokens.reshape(1, -1)
    tokens = torch.tensor(tokens, dtype=torch.long)
    
    if (len(tokens)> seq_len):
        tokens = tokens[-seq_len:]
    else:
        padding = torch.zeros((1,seq_len - len(tokens)), dtype= torch.long)
        tokens = torch.cat([padding, tokens], dim=1)
    tokens = tokens.to(device)
    print(initial_txt, end="")
    model.eval()
    
    for i in range(max_tokens):
        with torch.no_grad():
            logits = model(tokens)
            _, nxt_tkn = torch.max(logits, 1)
            
            print(tokenizer.decode([nxt_tkn]), end ="", flush=True)
            tokens = torch.cat([tokens , torch.reshape(nxt_tkn, (1,-1))], dim=1)
            tokens = tokens[-seq_len:]
            tokens=tokens.to(device)
    print("")

def create_dataloader(txt,seq_len=10, batch_size=5, shuffle=True):
    tokenizer = Tokenizer()
    tokens = tokenizer.encode(txt)

    dataset = GenTextDataset(tokens=tokens,
                             last_token_only=True,
                             seq_len=seq_len)

    dl = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, drop_last=True)
    return dl

def train_val_split(txt, train_ratio=0.9):
    txt_len = len(txt)
    train_len= int(txt_len * train_ratio)
    train_txt = txt[:train_len]
    val_txt = txt[train_len:]
    return train_txt, val_txt