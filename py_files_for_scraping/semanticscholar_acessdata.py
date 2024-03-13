from semanticscholar import SemanticScholar
from bs4 import BeautifulSoup
import requests
import json
from get_data import *
import pandas as pd
import time

def research_papers(faculty_name):
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    authors_name = faculty_name

    query_params = {
        "query": authors_name,
        'year': '2023',
        "fields": "paperCount,papers.title,papers.abstract,papers.openAccessPdf,papers.authors,papers.year,papers.publicationVenue,papers.isOpenAccess"
    }

 
    response = requests.get(url, params=query_params)

    if response.status_code == 200:
        #time.sleep(1)
        data = response.json()
        all_authors_data[faculty_name] = data

        papers = data.get('papers', [])
        
    
    else:
        print(f"Request failed with status code {response.status_code}")


def summary_research_papers(json_file_name, text_file_path):
    json_url = json_file_name
    with open(json_url, "r") as file:
        json_data = json.load(file)

    file_path = text_file_path
    with open(file_path, "w+", encoding='utf-8') as file:
        paper_number = 0
        for author, research_paper_data in json_data.items():
            for paper_data in research_paper_data["data"]:
                for data in paper_data["papers"]:
                    if data["year"] == 2023:
                        faculty_name = author
                        faculty_author_id = paper_data["authorId"]
                        paper_title = data["title"]
                        if data["isOpenAccess"] == True:
                            open_access_bool = data["isOpenAccess"]
                            publication_link = data["openAccessPdf"]
                            year_published = data["year"]
                            paper_abstract = data["abstract"]
                            paper_id = data["paperId"]
                            if publication_link is None:
                                publication_link = 'Its not open access'
                                url ='Not given'
                            else:
                                url = publication_link['url']
                            
                            r = requests.post('https://api.semanticscholar.org/graph/v1/paper/batch', params={'fields': 'tldr'}, json={"ids": [paper_id]})
                            data = r.json()
                            if data and isinstance(data, list) and len(data) > 0:
                                tldr_info = data[0].get('tldr', {})
                                if tldr_info == None:
                                    tldr_text = ''
                                else:
                                    tldr_text = tldr_info.get('text', '')

                            file.write(f"faculty_name: {faculty_name}\nfaculty_authorid: {faculty_author_id}\npaper_id: {paper_id}\npaper_title: {paper_title}\npublication_link: {url} \nyear_published: {year_published} \nabstract_paper:{paper_abstract}\nisOpenAccess: {open_access_bool}\nTL\DR: {tldr_text}\n================================\n")


    
def paper_pdf_links(json_file_name, file_path):
    json_url = json_file_name
    with open(json_url, "r") as file:
        json_data = json.load(file)

    with open(file_path, "w+", encoding='utf-8') as file:
        for author, research_paper_data in json_data.items():
            for paper_data in research_paper_data["data"]:
                for x in paper_data["papers"]:
                    if x["year"] == 2023:
                        publication_link = x["openAccessPdf"]
                        if publication_link is None:
                            publication_link = 'Its not open access'
                            url ='Not given'
                        else:
                            url = publication_link['url']
                            file.write(f"{url}\n")



all_authors_data = {}

url_faculty = 'https://web.archive.org/web/20231130214911/https://lti.cs.cmu.edu/directory/all/154/1'
url_faculty_page2 = 'https://web.archive.org/web/20231209211749/https://lti.cs.cmu.edu/directory/all/154/1?page=1'

faculty_names = get_workers_info(url_faculty)
faculty_names = get_workers_info(url_faculty_page2)+faculty_names

file_path = 'faculty_info.csv'
file_path_2 = 'faculty_info_2.csv'
df = pd.read_csv(file_path)
df2 = pd.read_csv(file_path_2)
col_name = 'Name'
faculty_name1 = df[col_name].tolist()
faculty_name2 = df2[col_name].tolist()
faculty_names = faculty_name1 + faculty_name2
print((faculty_name1[1]))

for faculty in faculty_names:
    print(faculty)
    research_papers(f'{faculty}')



#research_papers('Graham Neubig')

print('Faculty data pulling done')
json_file_name = 'json_file_faculties/grahamneubig.json'
text_file_path = 'metadata/grahamneubig'
filepath = 'paperlinks/grahamneubig'

with open(json_file_name, "w") as file:
    json.dump(all_authors_data, file, indent=4)

print('Created the JSON file')

summary_research_papers(json_file_name, text_file_path)
print('meta data created')

paper_pdf_links(json_file_name, filepath)
print('all research papers generated')
