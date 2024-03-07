
from langchain.docstore.document import Document
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Replicate
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import re



load_dotenv()


os.environ["REPLICATE_API_TOKEN"] = "r8_9rygkhbdp5p2opaveit7N1GuHR0HqKG3MTFYo"

def extract_questions_fixed(text):
    # Identifying the part of the text that contains the questions
    part_with_questions = text.split("QUESTIONS:\n")
    # Splitting this part into lines to individually process each line
    questions = []
    for q in part_with_questions:
        # print(q)
        lines = q.split('\n')
      # To store extracted questions
        for line in lines:
            # Adding a condition to include lines that seem like questions
            if line.strip() and line[0].isdigit():
                line = line.strip()
                line = re.sub("^[^A-Za-z]+", "", line)
                questions.append(line)
    return questions

def paragraphs_streaming_minLength(fileobj, min_length=2000):
    """Yield paragraphs from a file with a minimum length using a state machine approach."""
    IN_PARAGRAPH, BETWEEN_PARAGRAPHS = range(2)
    state = BETWEEN_PARAGRAPHS
    paragraph = []
    buffer = ""  # Initialize a buffer to accumulate paragraphs to meet the minimum length requirement

    for line in fileobj:
        if line.strip() == "":
            if state == IN_PARAGRAPH:
                # Add the current paragraph to the buffer and check its length
                buffer += ''.join(paragraph)
                paragraph = []  # Reset current paragraph
                if len(buffer) >= min_length:
                    # If the buffer meets the minimum length, yield it and reset the buffer
                    yield buffer
                    buffer = ""
            state = BETWEEN_PARAGRAPHS
        else:
            paragraph.append(line)
            state = IN_PARAGRAPH

    # After the loop, add any remaining content to the buffer
    if paragraph:
        buffer += ''.join(paragraph)

    # If the final buffer meets the minimum length requirement, yield it
    if len(buffer) >= min_length:
        yield buffer
    elif buffer:  # If there's content in the buffer but it doesn't meet the minimum length, still yield it
        yield buffer


prompt_template_questions = """
Your goal is to extract 3 question given the following context:  

------------
{text}
------------

The question must be contained entirely within the above text. Make sure not to lose any important information. 

Make sure the question is specific and detailed.

QUESTIONS:
"""

PROMPT_QUESTIONS = PromptTemplate(template=prompt_template_questions, input_variables=["text"])

refine_template_questions = """

We have received some practice questions to a certain extent: {existing_answer}.
We have the option to refine the existing questions or add new ones.
(only if necessary) with some more context below.
------------
{text}
------------

Given the new context, refine the original questions in English.
If the context is not helpful, please provide the original questions.

QUESTIONS:
"""

# answer_template = "GReturn an answer in one or two sentence, be concise."

answer_template = """
Given the question and context, 
Question: {question}
Context: {context}
Return an answer in one or two sentences, be short, concise and professional.
The answer must be contained strictly within the above context, do not make up any answer.
"""

ANS_PROMT = PromptTemplate(
    input_variables=["question","context"],
    template=answer_template,
)


REFINE_PROMPT_QUESTIONS = PromptTemplate(
    input_variables=["existing_answer", "text"],
    template=refine_template_questions,
)

# Initialize Large Language Model for question generation
llm_question_gen = Replicate(
        model="replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781",
        model_kwargs={"temperature": 0.2, "max_length": 100, "top_p": 1}
    )

# Initialize question generation chain
question_gen_chain = load_summarize_chain(llm=llm_question_gen, chain_type="refine", verbose=True,
                                              question_prompt=PROMPT_QUESTIONS, refine_prompt=REFINE_PROMPT_QUESTIONS)



paragraph_lists = []
############################
############################
############# File Entry
f_name = "/home/ubuntu/wenjinf/End-to-End-NLP-System/Scraped_pdf_file/PhD_Student_Handbook_2023-2024.txt"
with open(f_name, 'r') as f:
    for para in paragraphs_streaming_minLength(f):
        paragraph_lists.append(para)

docs_question_gen = [Document(page_content=t) for t in paragraph_lists]
questions_txt = ""
for t in paragraph_lists:
    doc = [Document(page_content=t)]
    q = question_gen_chain.run(doc)
    print("questions_YYDS: ", q)
    questions_txt+=q

extracted_questions_fixed = extract_questions_fixed(questions_txt)


# questions = question_gen_chain.run(docs_question_gen)

# extracted_questions_fixed = extract_questions_fixed(questions)
# # question_list = questions.split("\n")
# # question_list = question_list[2:]

# # Initialize Large Language Model for answer generation
llm_answer_gen = Replicate(
    model="replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781",
    model_kwargs={"temperature": 0.2, "max_length": 100, "top_p": 1})

# Create vector database for answer generation
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cuda"})
# Initialize vector store for answer generation
vector_store = Chroma.from_documents(docs_question_gen, embeddings)


# Initialize retrieval chain for answer generation
answer_gen_chain = RetrievalQA.from_chain_type(llm=llm_answer_gen, chain_type="stuff", chain_type_kwargs={"prompt": ANS_PROMT},
                                                   retriever=vector_store.as_retriever(k=2))

############################
############################
############# output Entry

output_file_path = "/home/ubuntu/wenjinf/End-to-End-NLP-System/Annotations/PhD_Student_Handbook_2023-2024.txt"
# print(len(question_list))

with open(output_file_path, "w", encoding="utf-8") as output_file:
    output_file.write("There are roughly" + str(len(extracted_questions_fixed)) + "Questions generated.")
    for i, question in enumerate(extracted_questions_fixed):
        output_file.write("Question-"+str(i)+": " + question + "\n")
        answer = answer_gen_chain.run(question)
        output_file.write("Answer: " + answer + "\n")
        output_file.write("\n")

