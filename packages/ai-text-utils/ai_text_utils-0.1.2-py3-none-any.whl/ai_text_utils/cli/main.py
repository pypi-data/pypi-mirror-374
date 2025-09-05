from ai_text_utils.text import Tokenizer, get_text_from_gutenberg_books, GenTextDataset, LSTMModel, create_dataloader, train_val_split
import torch
from torch.utils.data import DataLoader

def main():
    tkn = Tokenizer()

    tokens = tkn.encode("This is an example of tokenization")

    print(f'Tokens={tokens}')
    tokens = torch.Tensor(tokens).numpy()
    tokens=2065.5
    print(f'Getting text back from tokens = {tkn.decode(tokens)}')

    txt = get_text_from_gutenberg_books(start_book_id=2007, 
                                        num_books=1, 
                                        keep_headers=False)
    # 
    # say tokens =[1,2,3,4,5,6,7,8,9,10,11,12]
    # last_token_only=False generates data as ([1,2,3,4,5],[2,3,4,5,6]), ([7,8,9,10,11],[8,9,10,11,12])
    # last_token_only=True generates data as ([1,2,3,4,5],[6]), ([2,3,4,5,6],[7]), ([3,4,5,6,7],[8])
    '''
    tokens = tkn.encode(txt)
    dataset = GenTextDataset(tokens=tokens,last_token_only=False, seq_len=5)
    X,y = dataset[:2]
    print(f'last_token_only=False, X={X}, y={y}')
    dataset = GenTextDataset(tokens=tokens,last_token_only=True, seq_len=5)
    X,y = dataset[:2]
    print(f'last_token_only=True, X={X}, y={y}')
    '''

    train_txt, val_txt = train_val_split(txt, train_ratio=0.9)
    train_dl = create_dataloader(train_txt, batch_size=3, shuffle=True)
    val_dl=create_dataloader(val_txt, batch_size=3, shuffle=True)
    print(f'Train dl count: {len(train_dl)}, Val dl count: {len(val_dl)}')
    X, y = next(iter(train_dl))
    vocab_size=tkn.vocab_size()

    emb_size=100
    hidden_size=40
    model= LSTMModel(vocab_size=vocab_size,emb_size=emb_size,hidden_size=hidden_size)
    pred = model(X)
    _, pred = torch.max(pred, 1)
    print(f'vocab size = {vocab_size}, pred={pred}, actual={y}')

