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
for name in faculty_names:
    print(name)


# Define the API endpoint URL
url = "https://api.semanticscholar.org/graph/v1/author/search"
authors_name = "Graham Neubig"

# Define the required query parameters
query_params = {
    "query": authors_name,
    "sort": "2023-01-01",
    "year ": "2023",
    "fields": "paperCount,papers.title,papers.fieldsOfStudy"
}

# Make the GET request
response = requests.get(url, params=query_params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    filename = "data.json"
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
else:
    print(f"Request failed with status code {response.status_code}")