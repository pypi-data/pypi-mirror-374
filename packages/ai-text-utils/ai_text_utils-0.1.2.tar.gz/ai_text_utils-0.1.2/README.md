# AI Text Utils - GenTextDataset

This repository contains a reusable GenTextDataset, text extractor from gutenberg texts.

## Installation

```bash
pip install ai-text-utils
```

## Usage:

# extract text from gutenberg books

```python

from ai_text_utils.text import get_text_from_gutenberg_books

txt = get_text_from_gutenberg_books(start_book_id=2007, 
                                        num_books=1, 
                                        keep_headers=False)
```

## Details
- **Returns**: text start from book id 2007 
- **Arguments**: `num_books` tells number of books from which text has to be extracted starting from `start_book_id`. `keep_headers` tells if header info like author name , date of publish , copyright info, payment details , etc needs to be included in extracted text. setting `keep_headers` to False extracts only the content of the book. 

# convert text to tokens 
```python

from ai_text_utils.text import Tokenizer

tkn = Tokenizer()

tokens = tkn.encode("This is an example of tokenization")

print(f'Tokens={tokens}')
tokens = torch.Tensor(tokens).numpy()
print(f'Getting text back from tokens = {tkn.decode(tokens)}')

tokens = tkn.encode("This is an example of tokenization")
tokens = torch.Tensor(tokens)
print(f'Getting text back from tokens = {tkn.decode(tokens)}')

tokens = tkn.encode("This is an example of tokenization")
print(f'Getting text back from tokens = {tkn.decode(tokens)}')

tokens = tkn.encode("This is an example of tokenization")
tokens = tokens[-1]
print(f'Getting text back from tokens = {tkn.decode(tokens)}')
```

## Details
- **functions**: tokenizer has 2 functions `encode` and `decode`. `encode` converts text to list of tokens . `decode` converts list of tokens into text. `decode` function can take in list of tokens or numpy array of tokens or tensor array of tokens or single token of type int or type float and converts to text.



# convert token list to dataset

```python

from ai_text_utils.text import GenTextDataset, Tokenizer, get_text_from_gutenberg_books

txt = get_text_from_gutenberg_books(start_book_id=2007, 
                                        num_books=1, 
                                        keep_headers=False)

tokenizer = Tokenizer()
tokens = tokenizer.encode(txt)

dataset = GenTextDataset(tokens=tokens,
                        last_token_only=True,
                        seq_len=seq_len)
```

## Details
- **Returns**: GenTextDataset returns dataset with (input, output)
- **Arguments**: `tokens` is list of tokens . 
- **say tokens** =[1,2,3,4,5,6,7,8,9,10,11,12]
- **last_token_only=False** generates data as ([1,2,3,4,5],[2,3,4,5,6]), ([7,8,9,10,11],[8,9,10,11,12]). This type of dataset used for transformer next word prediction
- **last_token_only=True** generates data as ([1,2,3,4,5],[6]), ([2,3,4,5,6],[7]), ([3,4,5,6,7],[8]). This type of dataset used for LSTM next word prediction
    `seq_len` tells how many tokens in each input . in above example seq_len=5


# train val split and create dataloader

```python

from ai_text_utils.text import train_val_split, create_dataloader

train_txt, val_txt = train_val_split(txt, train_ratio=0.9)
train_dl = create_dataloader(train_txt,seq_len=10, batch_size=3, shuffle=True)
val_dl=create_dataloader(val_txt,seq_len=10, batch_size=3, shuffle=True)

```
## Details
Handy tools for splitting txt based on ratio and `create_dataloader` handy tool internally calls tokenizer and GenTextDataset . 
you can also use tokenizer and GenTextDataset  classes directly to create your own dataloader

