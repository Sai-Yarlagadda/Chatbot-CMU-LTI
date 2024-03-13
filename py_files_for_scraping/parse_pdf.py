import os
import pandas as pd
import PyPDF2

from dotenv import load_dotenv
import requests

import fitz #PYMU

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# from langchain_community.vectorstores import faiss
from langchain.chains.question_answering import load_qa_chain
from pdf2image import convert_from_path




def crop_image(element, pageObj):
    # Get the coordinates to crop the image from the PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    # Crop the page using coordinates (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Save the cropped page to a new PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Save the cropped PDF to a new file
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# Create a function to convert the PDF to images
def convert_to_images(input_file,):
    images = convert_from_path(input_file,500)
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")

def image_to_text(image_path):
    # Read the image
    img = Image.open(image_path)
    # Extract the text from the image
    text = pytesseract.image_to_string(img)
    return text



# def get_txt_pdf(file):
#     doc_content = ""
#     if file.startswith("https"):
#         response = requests.get(file)
#         if response.status_code == 200:
#             pdf_content = response.content
#             doc = fitz.open(stream=pdf_content, filetype="pdf")
#     else:
#         doc = fitz.open(file)
#     n = doc.page_count
#     for i in range(0, n):
#         page_n = doc.load_page(i)
#         tabs = page_n.find_tables()
#         page_content = page_n.get_text("blocks")
#         page_info = ""
#         for element in page_content:
            
#             if element[6] == 0:
#                 page_info += element[4]
#             else:
#                 pageObj = pdfReaded.pages[i]
#                 crop_image(element, pageObj)
#                 # Convert the cropped pdf to an image
#                 convert_to_images('cropped_image.pdf')
#                 # Extract the text from the image
#                 image_text = image_to_text('PDF_image.png')
#                 page_info += image_text

#         doc_content += page_info + "\n"
#     return doc_content




data_path = "/Users/wenjinfu/Desktop/NLP/End-to-End-NLP-System/pdf_files" # path to the folder where pdf files are available

for file in os.listdir(data_path):
    if not file.endswith("pdf"): continue
    file_name = os.path.join(data_path,file)

    # create a PDF file object
    pdfFileObj = open(file_name, 'rb')
    # create a PDF reader object
    print("read file: ", file_name)
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)


    # read doc
    doc = fitz.open(file_name)
    #extract page num
    n = doc.page_count

    doc_content = ""
    for i in range(0, n):
        
        page_n = doc.load_page(i)
        tabs = page_n.find_tables()
        page_content = page_n.get_text("blocks")
        page_info = ""
        for element in page_content:
            
            if element[6] == 0:
                page_info += element[4]
            else:
                pageObj = pdfReaded.pages[i]
                crop_image(element, pageObj)
                # Convert the cropped pdf to an image
                convert_to_images('cropped_image.pdf')
                # Extract the text from the image
                image_text = image_to_text('PDF_image.png')
                page_info += image_text

        doc_content += page_info + "\n"
    
    
    txt_file = "/Users/wenjinfu/Desktop/NLP/End-to-End-NLP-System/Scraped_pdf_file/"+file.split("pdf")[0]+'txt'
    print("saved file: ", txt_file)
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write(doc_content)








# text_splitter = CharacterTextSplitter(
#     separator="\n",
#     chunk_size = 800,
#     chunk_overlap = 200,
#     length_function = len
# )

# texts = text_splitter.split_text(doc_content)


# print(texts)

# huggingface_embeddings = HuggingFaceBgeEmbeddings(
#     model_name="BAAI/bge-small-en-v1.5",  # alternatively use "sentence-transformers/all-MiniLM-l6-v2" for a light and faster experience.
#     model_kwargs={'device':'cpu'}, 
#     encode_kwargs={'normalize_embeddings': True}
# )


## Retrieval System for vector embeddings



# Use similarity searching algorithm and return 3 most relevant documents.
# retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
