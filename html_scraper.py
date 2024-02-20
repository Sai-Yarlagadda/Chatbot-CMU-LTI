from bs4 import BeautifulSoup
import requests
import csv

'''def get_faculty_info(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    view_content_div = soup.find(class_='view-content')
    elements = view_content_div.find_all('h2')
    faculty_names = [f_name.get_text() for f_name in elements]
    print(faculty_names)
    faculty_info = view_content_div.find_all(class_='views-field-field-computed-prof-title')
    faculty_positions = [info.get_text().strip() for info in faculty_info]
    print(faculty_positions)

    return faculty_names'''

def get_faculty_info(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    view_content_div = soup.find(class_='view-content')
    faculty_info = view_content_div.find_all(class_='views-field-field-computed-prof-title')
    elements = view_content_div.find_all('h2')
    all_hyperlinks = view_content_div.find_all('a', href=True)
    emails = []
    for link in all_hyperlinks:
        if 'mailto:' in link['href']:
            emails.append(link['href'].split(':')[1])

    research_area = view_content_div.find_all(class_='views-field-field-research-areas')
    research_areas = []
    for r_area in research_area:
        
        print(r_area)
        if r_area:
            research_areas.append(r_area.get_text().strip())
        else:
            research_areas.append("")



    
    for i in range(len(elements)):
        faculty_name = elements[i].get_text()
        faculty_position = faculty_info[i].get_text().strip()
        faculty_email = emails[i]
        print(faculty_name)
        print(faculty_position)
        print(faculty_email)
        print(research_areas[i])
        print()

url_faculty_1 = 'https://lti.cs.cmu.edu/directory/all/154/1'
url_faculty_2 = 'https://lti.cs.cmu.edu/directory/all/154/1?page=1'
url_affiliated_faculty = 'https://lti.cs.cmu.edu/directory/all/154/2728'
url_adjunct_faculty = 'https://lti.cs.cmu.edu/directory/all/154/200'
url_schedule_of_classes = 'https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_spring.htm'


get_faculty_info(url_faculty_1)
get_faculty_info(url_faculty_2)