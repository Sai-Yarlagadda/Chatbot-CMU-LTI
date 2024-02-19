from semanticscholar import SemanticScholar
from bs4 import BeautifulSoup
import requests, json
from faculty_list import *



url_faculty = 'https://lti.cs.cmu.edu/directory/all/154/1'
url_affiliated_faculty = 'https://lti.cs.cmu.edu/directory/all/154/2728'
url_adjunct_faculty = 'https://lti.cs.cmu.edu/directory/all/154/200'
faculty_names = get_workers_info(url_faculty)
faculty_names = get_workers_info(url_affiliated_faculty) + faculty_names
faculty_names = get_workers_info(url_adjunct_faculty) + faculty_names

def research_papers(faculty_name):
    # Define the API endpoint URL
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    authors_name = faculty_name

    # Define the required query parameters
    query_params = {
        "query": authors_name,
        'year': '2023-',
        "fields": "paperCount,papers.title,papers.fieldsOfStudy"
    }

    # Make the GET request
    response = requests.get(url, params=query_params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        '''filename = f"{faculty_name}_data.json"
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)'''
        all_authors_data[faculty_name] = data
    else:
        print(f"Request failed with status code {response.status_code}")

all_authors_data = {}

for faculty in faculty_names:
    research_papers(faculty)

with open("research_papers_faculty.json", "w") as file:
    json.dump(all_authors_data, file, indent=4)
