import os
import requests
from bs4 import BeautifulSoup
import re

def get_text_from_gutenberg_books(start_book_id=1660, num_books=10, keep_headers=False):
    text=""
    for i in range(num_books):
        id = start_book_id+i
        single_book_txt = download_gutenberg_book(book_id=id,
                                                  output_file="sample"+str(id),
                                                  keep_headers=keep_headers)
        text += single_book_txt
    return text

def download_gutenberg_book(book_id,output_file, save_dir="gutenberg_books", keep_headers=False):
    """
    Download a text book from Project Gutenberg by book ID.
    
    Args:
        book_id (str): The Project Gutenberg book ID (e.g., '12345')
        save_dir (str): Directory to save the downloaded book
    """
    # Create save directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Construct URL for the book's text file
    base_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    output_file = os.path.join(save_dir, output_file)
    try:

        if not os.path.exists(output_file):
            try:

                # Send request to get the book
                response = requests.get(base_url)
                response.raise_for_status()  # Check for HTTP errors
                
                # Parse HTML to get book title
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.text if soup.title else f"book_{book_id}"
                # Clean title for filename
                title = "".join(c for c in title if c.isalnum() or c in (' ',)).rstrip()

                txt= response.text
                if (txt is not None):
                    if(not keep_headers):
                        txt = compact_gutenberg_text(txt)
                else: 
                    txt=""
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(txt)
                print(f"Downloaded book {book_id} to {output_file}")
                return txt
            except Exception as e:
                print(f"Error downloading book {book_id}: {e}")
        else:
            print(f"File {output_file} already exists. Skipping download.")
            with open(output_file, 'r', encoding='utf-8') as file:
                text = file.read()
                return text
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading book {book_id}: {e}")
        return ""

def compact_gutenberg_text(text):
    """
    Extracts main content from Project Gutenberg eBook and removes excessive newlines
    while preserving paragraph structure.
    """

    # Find main content between standard Gutenberg markers
    start_pattern = re.compile(
        r'\*\*\*\s*START OF (?:THIS|THE) PROJECT GUTENBERG EBOOK.*?\*\*\*',
        re.IGNORECASE | re.DOTALL
    )
    end_pattern = re.compile(
        r'\*\*\*\s*END OF (?:THIS|THE) PROJECT GUTENBERG EBOOK.*?\*\*\*|'
        r'End of (?:the )?Project Gutenberg(?: eBook)?.*',
        re.IGNORECASE | re.DOTALL
    )

    start_match = start_pattern.search(text)
    end_match = end_pattern.search(text)

    if not start_match or not end_match:
        raise ValueError("Could not find Gutenberg start/end markers")

    content = text[start_match.end():end_match.start()]

    # Clean up the content
    # 1. Remove common metadata lines
    content = re.sub(r'^\s*Produced by.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\[Illustration:.*\]\s*$', '', content, flags=re.MULTILINE)
    
    # 2. Normalize whitespace - compact multiple newlines while preserving paragraphs
    # First replace 3+ newlines with double newline (paragraph break)
    content = re.sub(r'\n{3,}', '\n\n', content)
    # Then replace remaining double newlines with single ones (within paragraphs)
    content = re.sub(r'([^\n])\n{2}([^\n])', r'\1\n\2', content)
    
    # 3. Remove space at start/end of lines
    content = '\n'.join(line.strip() for line in content.split('\n'))
    
    # 4. Remove completely empty lines (but keep single newlines between paragraphs)
    content = re.sub(r'\n\s*\n', '\n\n', content)
    

    return content.strip()
