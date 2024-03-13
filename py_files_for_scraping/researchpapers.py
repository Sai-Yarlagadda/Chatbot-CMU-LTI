import requests
import fitz  


def research_paper(url, i):
    try:
        response = requests.get(url, timeout=10)
        with open('research_paper.pdf', 'wb') as file:
            file.write(response.content)
        text = ''
        try:
            with fitz.open('research_paper.pdf') as pdf_document:
                for page_number in range(pdf_document.page_count):
                    page = pdf_document[page_number]
                    text += page.get_text()
            with open(f'researchpapers\{i}', "w+", encoding='utf-8') as file:
                file.write(f"{text}\n")
        except:
            with open(f'researchpapers\{i}', "w+", encoding='utf-8') as file:
                file.write(f'Link is broken \n')
            print(f'Link is broken for {i}')

    except:
        with open(f'researchpapers\{i}', "w+", encoding='utf-8') as file:
            file.write(f'Link is broken \n')
        print(f'Connection Error')
        links_to_reget.append(url)

#url = 'http://arxiv.org/pdf/2306.17842'
with open('paperlinks\paperlinks', 'r') as file:
    paper_links_file = file.readlines()

links_list = []
for paper_links in paper_links_file:
    line = paper_links.strip()
    links_list.append(line)

links_to_reget = []
for i, links in enumerate(links_list):
    print(i)
    research_paper(links, i)
