# Necessary inputs

import os
import time
import torch
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.prompts import ChatPromptTemplate, format_document
from langchain.prompts.prompt import PromptTemplate
import requests
import sys
from langchain_core.prompts import ChatPromptTemplate, format_document
from langchain.prompts.prompt import PromptTemplate

# Setting the Together API Key
os.environ["TOGETHER_API_KEY"] = "fcb5dca384064dce53475051ef6c784761895841b000c09e5611b0344b5466c4"  # Please do not run it with this API Key.

# Calling the created embedding vector database
model_name = "BAAI/bge-large-en-v1.5"
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model_norm = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': DEVICE},
    encode_kwargs=encode_kwargs)

db3 = Chroma(persist_directory="db", embedding_function=model_norm)

# Retriever settings
retriever = db3.as_retriever(search_kwargs={"k": 100})

# Defining the LLM (LLaMa2 - 70B - Chat) using Together API
def get_answer(input_text) -> str:
    url = 'https://api.together.xyz/inference'
    headers = {
      'Authorization': 'Bearer ' + os.environ["TOGETHER_API_KEY"],
      'accept': 'application/json',
      'content-type': 'application/json'
    }
    data = {
      "model": "togethercomputer/llama-2-70b-chat",
      "prompt": input_text,
      "max_tokens": 100,
      "temperature": 0.7,
      "top_p": 0.7,
      "top_k": 50,
      "repetition_penalty": 1
    }
    response = requests.post(url, json=data, headers=headers)
    #print(response.json())
    text = response.json()['output']['choices'][0]['text']
    print(text)
    return text

# Defining helper functions
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

def combine_documents_2(docs, document_separator="\n\n"):
    combined_docs = []
    for doc in docs:
        combined_docs.append(doc[1])  # Extracting page content from each inner list
    return document_separator.join(combined_docs)

def split_questions(string, delimiter='?'):
    questions = string.split(delimiter)
    questions = [question.strip().split(". ", 1)[-1] + delimiter for question in questions]
    return questions

# Reference (https://api.python.langchain.com/en/latest/_modules/langchain/retrievers/multi_query.html#:~:text=def%20_unique_documents(documents%3A%20Sequence%5BDocument%5D)%20%2D%3E%20List%5BDocument%5D%3A%0A%20%20%20%20return%20%5Bdoc%20for%20i%2C%20doc%20in%20enumerate(documents)%20if%20doc%20not%20in%20documents%5B%3Ai%5D%5D)

def _unique_documents(documents):
    return [doc for i, doc in enumerate(documents) if doc not in documents[:i]]

# Using only the retriever

with open('questions.txt', 'r') as file:
    questions = file.readlines()
for question in questions:
    docs = retriever.get_relevant_documents(question)

    prompt_start = """
    You are an assistant for question-answering tasks and the questions are related to Carnegie Mellon University. Use the following pieces of retrieved context to answer the question. Do not exceed one sentence for the answer. Do not be verbose when generating the answer. Give out the answer directly even if it does not form a coherent sentence.
    """

    context = combine_documents(docs[:3])
    input_text = prompt_start + "Question: " + question + "Context: " + context + "Answer: "
    time.sleep(1)
    print(question)

    answer = get_answer(input_text)
    with open('rag_system_answers.txt', 'a', encoding='utf-8') as output_file:
        output_file.write(f'{answer}\n==================\n')


# Using Retriever + Reranking

# Define the reranker model
        
from FlagEmbedding import FlagReranker
reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)

with open('questions.txt', 'r', encoding = 'utf-8') as file:
    questions = file.readlines()
for question in questions:
    docs = retriever.get_relevant_documents(question)

    prompt_start = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. Do not exceed one sentence for the answer. Do not be verbose when generating the answer. Give out the answer directly even if it does not form a coherent sentence.
    """
    docs_to_rerank = []
    for i in range(len(docs)):
        docs_to_rerank.append([question, str(docs[i])])
    scores = reranker.compute_score(docs_to_rerank)

    #sorting documents based on scores given by reranker
    combined_data = list(zip(docs_to_rerank, scores))
    sorted_data = sorted(combined_data, key=lambda x: x[1], reverse=True)
    sorted_docs_to_rerank, sorted_scores = zip(*sorted_data)
    top_k_docs = sorted_docs_to_rerank[:3]
    context = combine_documents_2(top_k_docs)

    input_text = prompt_start + "Question: " + question + "Context: " + context + "Answer: "
    print(question)
    time.sleep(1)

    answer = get_answer(input_text)
    print("=====================")
    with open('rag_with_reranker_answers.txt', 'a', encoding = 'utf-8') as output_file:
        output_file.write(f'{answer}\n==================\n')


# Using Retriever + Reranking + Multi query retriever

delimiter = '?'

with open('questions.txt', 'r') as file:
    questions = file.readlines()
    
for question in questions:
    
    input_text_for_ques = f"""
    [TASK]: Write the below question in 3 different ways.
    [QUESTION]: {question}
    """
    
    diff_questions = get_answer(input_text_for_ques)
    
    paraphrased_ques = split_questions(diff_questions, delimiter)
    paraphrased_ques = paraphrased_ques[:-1]
    print(paraphrased_ques)
    
    all_docs = []
    for single_question in paraphrased_ques:
        all_docs.extend(retriever.get_relevant_documents(single_question))
        
    all_docs.extend(retriever.get_relevant_documents(question))
    
    unique_docs = _unique_documents(all_docs)

    prompt_start = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. Do not exceed one sentence for the answer. Do not be verbose when generating the answer. Give out the answer directly even if it does not form a coherent sentence.
    """
    
    docs_to_rerank = []
    for i in range(len(unique_docs)):
        docs_to_rerank.append([question, str(unique_docs[i])])
    scores = reranker.compute_score(docs_to_rerank)

    #sorting documents based on scores given by reranker
    combined_data = list(zip(docs_to_rerank, scores))
    sorted_data = sorted(combined_data, key=lambda x: x[1], reverse=True)
    sorted_docs_to_rerank, sorted_scores = zip(*sorted_data)
    top_k_docs = sorted_docs_to_rerank[:3]
    context = combine_documents_2(top_k_docs)

    input_text = prompt_start + "Question: " + question + "Context: " + context + "Answer: "
    print(question)
    time.sleep(1)

    answer = get_answer(input_text)
    print("=====================")
    with open('rag_with_reranker_with_multiquery_answers.txt', 'a', encoding = 'utf-8') as output_file:
        output_file.write(f'{answer}\n==================\n')


# Using Retriever + Reranking + Multi query retriever + Few-shot prompting

delimiter = '?'

with open('D:\\Masters\\2nd Semester\\Advanced Natural Language Processing\\Homeworks\\HW2\\data\\test\\questions.txt', 'r') as file:
    questions = file.readlines()
    
for question in questions:
    
    input_text_for_ques = f"""
    [TASK]: Rewrite the following question in three distinct formulations.
    [ORIGINAL QUESTION]: {question}
    """
    
    diff_questions = get_answer(input_text_for_ques)
    
    paraphrased_ques = split_questions(diff_questions, delimiter)
    paraphrased_ques = paraphrased_ques[:-1]
    print(paraphrased_ques)
    
    all_docs = []
    for single_question in paraphrased_ques:
        all_docs.extend(retriever.get_relevant_documents(single_question))
        
    all_docs.extend(retriever.get_relevant_documents(question))
    
    unique_docs = _unique_documents(all_docs)

    prompt_start = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. Do not exceed one sentence for the answer. Keep the answer concise even if it lacks coherence. Provide the specific information requested without using full sentences.
    
    Here are some examples to illustrate the answer format:
    
    Query: Graham Neubig's title?
    Answer: Associate Professor
    
    Query: Jamie Callan's author id?
    Answer: 144987107
    
    Query: Bryan Burtner's office location?
    Answer: 6413 TCS Hall
    """
    
    docs_to_rerank = []
    for i in range(len(unique_docs)):
        docs_to_rerank.append([question, str(unique_docs[i])])
    scores = reranker.compute_score(docs_to_rerank)

    #sorting documents based on scores given by reranker
    combined_data = list(zip(docs_to_rerank, scores))
    sorted_data = sorted(combined_data, key=lambda x: x[1], reverse=True)
    sorted_docs_to_rerank, sorted_scores = zip(*sorted_data)
    top_k_docs = sorted_docs_to_rerank[:3]
    context = combine_documents_2(top_k_docs)

    input_text = prompt_start + "Question: " + question + "Context: " + context + "Answer: "
    print(question)
    time.sleep(1)

    answer = get_answer(input_text)
    print("=====================")
    with open('rag_with_reranker_with_multiquery_with_few_shot_answers.txt', 'a', encoding = 'utf-8') as output_file:
        output_file.write(f'{answer}\n==================\n')

"""
Few shot prompting gave extremely bad results, so we ignore it. This may be because of the way that we define our examples.
We have defined QA pairs directly when giving the examples, but have not defined the context for them.
This seems to be confusing the model.
"""

"""
We run the same script for the test set provided by the instructors. We just changed the paths of the questions.txt and the
generated answers file accordingly.
"""
