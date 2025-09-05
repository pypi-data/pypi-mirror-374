import torch.nn as nn
import torch

class LSTMModel(nn.Module):
    def __init__(self, vocab_size, emb_size=300, hidden_size=200, pretrained_embeddings=None):
        super().__init__()
        if (pretrained_embeddings) :
            self.emb = nn.Embedding.from_pretrained(pretrained_embeddings)
        else:
            self.emb= nn.Embedding(vocab_size, emb_size)
        
        self.attn = AttnModule(emb_size)
        self.lstm = nn.LSTM(emb_size,hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, X):
        X = self.emb(X)
        X = self.attn(X)
        output, _ = self.lstm(X)
        lstm_out = output[:, -1,:]
        X=self.fc(lstm_out)
        return X

class AttnModule(nn.Module):
    def __init__(self, emb_size=300):
        super().__init__()
        self.emb_size=emb_size

    def forward(self, X):
        scores = X @ X.transpose(-2, -1)
        scaled_scores = scores / (self.emb_size ** 0.5)
        attn_wts = torch.softmax(scaled_scores, dim=-1)
        X = attn_wts @ X
        return X
