from bs4 import BeautifulSoup
import requests

def get_workers_info(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html')
    #print(soup.prettify())
    view_content_div = soup.find(class_='view-content')
    elements = view_content_div.find_all('h2')
    workers_names = [worker_name.get_text() for worker_name in elements]

    return workers_names



#all urls
url_faculty = 'https://lti.cs.cmu.edu/directory/all/154/1'
url_affiliated_faculty = 'https://lti.cs.cmu.edu/directory/all/154/2728'
url_adjunct_faculty = 'https://lti.cs.cmu.edu/directory/all/154/200'



