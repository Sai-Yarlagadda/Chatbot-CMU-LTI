# Necessary imports

import os
import torch
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Load the embedding model from hugging face

model_name = "BAAI/bge-large-en-v1.5"
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_norm = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': DEVICE},
    encode_kwargs=encode_kwargs)

# Load all the knowledge resource

loader = DirectoryLoader('C:\\Users\\Akshay Badagabettu\\Downloads\\Raw data Assignment 2-20240310T203323Z-001\\Raw data Assignment 2', glob="./*.txt")
docs = loader.load()

print(len(docs))

# Create the chunks

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)
texts = text_splitter.split_documents(docs)
print(len(texts))

# Embed it

embedding = model_norm
persist_directory = 'db'
vectordb = Chroma.from_documents(documents=texts,
                                 embedding=embedding,
                                 persist_directory=persist_directory)

# Testing out the embedding

retriever = vectordb.as_retriever(search_kwargs={"k": 100})
docs = retriever.get_relevant_documents("What are the dates for the Spring Carnival 2024?")
print(docs)
