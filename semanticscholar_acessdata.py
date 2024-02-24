from semanticscholar import SemanticScholar
from bs4 import BeautifulSoup
import requests
import json
from get_data import *

def research_papers(faculty_name):
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    authors_name = faculty_name

    query_params = {
        "query": authors_name,
        'year': '2023-',
        "fields": "paperCount,papers.title,papers.abstract,papers.openAccessPdf,papers.authors,papers.year,papers.publicationVenue"
    }

    response = requests.get(url, params=query_params)


    if response.status_code == 200:
        data = response.json()
        all_authors_data[faculty_name] = data

        papers = data.get('papers', [])

    else:
        print(f"Request failed with status code {response.status_code}")

def summary_research_papers(json_file_name):
    json_url = json_file_name
    with open(json_url, "r") as file:
        json_data = json.load(file)

    file_path = "questions_answer_pair.txt"
    with open(file_path, "w+", encoding='utf-8') as file:
        paper_number = 0
        for author, research_paper_data in json_data.items():
            for paper_data in research_paper_data["data"]:
                faculty_name = author
                faculty_author_id = paper_data["authorId"]
                for x in paper_data["papers"]:
                    paper_title = x["title"]
                    publication_link = x["openAccessPdf"]
                    year_published = x["year"]
                    paper_abstract = x["abstract"]
                    if publication_link is None:
                        publication_link = 'Its not open access'
                        url ='Not given'
                    else:
                        url = publication_link['url']
                    file.write(f"faculty_name: {faculty_name}\nfaculty_authorid: {faculty_author_id}\npaper_title: {paper_title}\npublication_link: {url} \nyear_published: {year_published} \nabstract_paper:{paper_abstract}\n================================\n")

def paper_pdf_links(json_file_name):
    json_url = json_file_name
    with open(json_url, "r") as file:
        json_data = json.load(file)

    file_path = "research_papers_links.txt"

    with open(file_path, "w+", encoding='utf-8') as file:
        for author, research_paper_data in json_data.items():
            for paper_data in research_paper_data["data"]:
                for x in paper_data["papers"]:
                    publication_link = x["openAccessPdf"]
                    if publication_link is None:
                        publication_link = 'Its not open access'
                        url ='Not given'
                    else:
                        url = publication_link['url']
                        file.write(f"{url}\n")


all_authors_data = {}

url_faculty = 'https://lti.cs.cmu.edu/directory/all/154/1'
url_affiliated_faculty = 'https://lti.cs.cmu.edu/directory/all/154/2728'
url_adjunct_faculty = 'https://lti.cs.cmu.edu/directory/all/154/200'


faculty_names = get_workers_info(url_faculty)
faculty_names = get_workers_info(url_affiliated_faculty) + faculty_names
faculty_names = get_workers_info(url_adjunct_faculty) + faculty_names

for faculty in faculty_names:
    research_papers(faculty)

with open("research_papers_faculty.json", "w") as file:
    json.dump(all_authors_data, file, indent=4)

summary_research_papers('research_papers_faculty.json')
paper_pdf_links('research_papers_faculty.json')
