from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

    #research_area = view_content_div.find_all(class_='views-field-field-research-areas')
    research_areas = []
    phone_numbers = []
    offices = []
    for element in faculty_info:
        research_area = element.find_next_sibling(class_='views-field-field-research-areas')
        phone_number = element.find_next_sibling(class_='views-field views-field-field-computed-phone')
        office = element.find_next_sibling(class_='views-field views-field-field-computed-building')
        if research_area:
            r = research_area.get_text().strip()
            if r.startswith('Research Areas:'):
                r = r.replace("Research Areas:", "").strip()
            research_areas.append(r)
        else:
            research_areas.append("")
        if phone_number:
            p = phone_number.get_text().strip()
            if p.startswith('Phone:'):
                p = p.replace("Phone:", "").strip()
            phone_numbers.append(p)
        else:
            phone_numbers.append("")
        if office:
            office_text = office.get_text().strip()
            if office_text.startswith("Office:"):
                office_text = office_text.replace("Office:", "").strip()
            offices.append(office_text)
        else:
            offices.append("")

    
    '''for i in range(len(elements)):
        faculty_name = elements[i].get_text()
        faculty_position = faculty_info[i].get_text().strip()
        faculty_email = emails[i]
        print(faculty_name)
        print(faculty_position)
        print(faculty_email)
        print(research_areas[i])
        print(offices[i])
        print(phone_numbers[i])
        print()'''
    
    with open('research_staff_info.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Position', 'Email', 'Research Area', 'Office', 'Phone Number'])
        for i in range(len(elements)):
            faculty_name = elements[i].get_text()
            faculty_position = faculty_info[i].get_text().strip()
            faculty_email = emails[i]
            writer.writerow([faculty_name, faculty_position, faculty_email, research_areas[i], offices[i], phone_numbers[i]])

def get_text(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    text = soup.get_text()
    with open('kiltie_band.txt', 'w', encoding='utf-8') as file:
        file.write(text)


def get_tables(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    tables = soup.find_all('table')

    for index, table in enumerate(tables, 1):
        filename = f"table_{index}.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all(['td', 'th'])
                row_data = [column.get_text().strip() for column in columns]
                writer.writerow(row_data)
        print(f"Table {index} content has been written to {filename} successfully.")


url_faculty_1 = 'https://lti.cs.cmu.edu/directory/all/154/1'
url_faculty_2 = 'https://lti.cs.cmu.edu/directory/all/154/1?page=1'
url_affiliated_faculty = 'https://lti.cs.cmu.edu/directory/all/154/2728'
url_adjunct_faculty = 'https://lti.cs.cmu.edu/directory/all/154/200'
lti_staff_1 = 'https://lti.cs.cmu.edu/directory/all/154/2'
lti_staff_2 = 'https://lti.cs.cmu.edu/directory/all/154/2?page=1'
lti_admin_staff = 'https://lti.cs.cmu.edu/directory/all/154/2731'
lti_research_staff = 'https://lti.cs.cmu.edu/directory/all/154/2730'
spring_carnival = 'https://web.cvent.com/event/ab7f7aba-4e7c-4637-a1fc-dd1f608702c4/websitePage:645d57e4-75eb-4769-b2c0-f201a0bfc6ce?locale=en' #bad website provided
programs = 'https://lti.cs.cmu.edu/learn'
spring_carnival_2 = 'https://www.cmu.edu/engage/alumni/events/campus/spring-carnival/schedule/index.html'
commencement = 'https://www.cmu.edu/commencement/schedule/index.html'
twentyfive_great_things = 'https://www.cs.cmu.edu/scs25/25things'
history = 'https://www.cs.cmu.edu/scs25/history'
history_2 = 'https://www.cmu.edu/about/history.html'
buggy = 'https://www.cmu.edu/news/stories/archives/2019/april/spring-carnival-buggy.html'
tartan_facts = 'https://athletics.cmu.edu/athletics/tartanfacts' #TODO: 403 Error - Fix this
scotty = 'https://athletics.cmu.edu/athletics/mascot/about'
kiltie_band = 'https://athletics.cmu.edu/athletics/kiltieband/index'

#get_faculty_info(lti_research_staff)
#get_tables(programs)
get_text(kiltie_band)
