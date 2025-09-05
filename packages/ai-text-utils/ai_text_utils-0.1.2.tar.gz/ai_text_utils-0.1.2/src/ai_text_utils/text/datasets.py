from torch.utils.data import Dataset
import torch
import numpy as np

class GenTextDataset(Dataset):
    def __init__(self, tokens, last_token_only=False, seq_len=50):
        sequences=[]
        stride = 1
        if (not last_token_only):
            stride=seq_len
        for i in range(0, len(tokens)- seq_len, stride):
            seq = tokens[i:i+seq_len]
            sequences.append(seq)
        sequences = np.array(sequences)
        X= sequences[:,:-1]
        if (last_token_only):
            y=sequences[:,-1]
        else:
            y=sequences[:,1:]
        self.X = torch.from_numpy(X).long()
        self.y= torch.from_numpy(y).long()

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self,idx):
        return self.X[idx], self.y[idx]