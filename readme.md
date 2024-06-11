# Cohere Aromatica

This is an organic chemistry chatbot which answers all of yoiur organic chemistry problems.
Simply upload any organic chemistry reference (for example, Simek/Wade 9th Edition Organic Chemistry)
as a PDF file and paste your API key. Then, ask your questions and watch magic happen!

# Features

## RAG

Retrieval Augmented Generation (RAG) is used to extract relevant information from textbook references.
You must manually adjust the compression factor in the file `rag.py` to prevent the script from attempting
to parse more chunks than the limit.

## Instructions

An instructions file for the organic chemistry chatbot is included. It includes detailed instructions for responses as well as n-shot learning examples with specific Q/A instances for the chatbot to learn from. You may modify the instruction if you would like to adjust the functionality.