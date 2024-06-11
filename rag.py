"""
Retrieval Augmented Generation.
"""

import cohere
import os
import glob
import PyPDF2

def extract_ranked_citations(*,
                             client: cohere.Client,
                             source: str,
                             query: str,
                             model: str = 'rerank-english-v3.0',
                             n_pages_per_chunk: int = 1,
                             n_results: int = 10) -> list:
    """
    Retrieve text from all PDF files in a given folder and select the most relevant.
    ### Parameters (named)
    - `client`: `cohere.Client` - The Cohere client object.
    - `source`: `str` - The path to the folder containing the PDF files.
    - `query`: `str` - The query to search for in the PDF files.
    - `model`: `str` - The model to use for ranking the results. Default: `'rerank-english-v3.0'`.
    - `n_pages_per_chunk`: `int` - The number of pages to group together in a single chunk. 
       Used for big documents. Default: `1` (no compression).
    - `n_results`: `int` - The number of top results to select. Default: `10` most relevant text chunks.
    ### Return
    - `ranked_results`: `list[dict]` - Formatted as `[{'title': str, 'content': str}]`.
    """
    # Assign the Cohere API client
    co = client
    # Identify all PDF files in the directory
    pdf_files = glob.glob(f'{source}/*.pdf')
    # Initialize a list to store the sources
    sources = []
    # Iterate through PDFs
    for pdf_file in pdf_files:
        pdf_name = os.path.basename(pdf_file) # PDF name
        pdfFileObj = open(pdf_file, 'rb') # Open the PDF file
        pdfReader = PyPDF2.PdfReader(pdfFileObj) # Initialize a reader
        words = [] # Store text chunks
        for page_index, page in enumerate(pdfReader.pages): # Iterate through pages
            # Extract text from the page, including information about the source file title and page number
            text = f'Text chunk from file {pdf_name}, page {page}\n\n{page.extract_text()}'
            words.append(text)
        pdfFileObj.close()
        # Compression of text chunks to fit within 10000-chunk rerank limit
        compressed = []
        for i in range(0, len(words), n_pages_per_chunk):
            compressed.append('\n'.join(words[i:i + n_pages_per_chunk]))
        sources.extend([{'title': pdf_name, 'content': content} for content in compressed])
    # Rerank the sources based on the relevance to the query
    rerank = co.rerank(model = model,
                       query = query,
                       documents = sources,
                       top_n = n_results,
                       rank_fields = ['content'],
                       return_documents = True)
    # Restructure the rerank results for chat_stream-compatible format
    ranked = []
    for item in rerank.results:
        ranked.append({'content': item.document.content, 
                       'title': item.document.title})
    return ranked