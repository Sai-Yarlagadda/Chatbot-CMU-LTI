# End-to-End-NLP-System
- Abstract
  As a part of this assignment we worked on building a Retrieval Augmented Generation system that is capable of answering questions related to various facts about Carnegie Mellon University(CMU) and Language Technologies Institute (LTI). This is one particular topic that requires domain knowledge related to CMU and LTI for answering questions. Our RAG system addresses LLM's domain knowledge limitations by compiling documents relevant to the questions at hand. The core of our endeavor involved extensive data preparation and annotation phase, employing both automated tools and manual efforts. Incorporating both a multiquery retriever and a reranker into the RAG system yielded statistically significant results when compared to utilizing only a retriever in the RAG framework. This model had given a F1 score of 0.4161, which is 1.57 times better than the F1 score of a retriever only model.

What each folder on the github contains:
-Annotations folder: 
  - This folder contains the initial annotations we collected based on the data scraped from sources related to CMU and LTI department.  
-Embeddings folder:
  -
