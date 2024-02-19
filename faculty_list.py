from bs4 import BeautifulSoup
import requests
import csv

def get_workers_info(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html')
    #print(soup.prettify())
    view_content_div = soup.find(class_='view-content')
    elements = view_content_div.find_all('h2')
    workers_names = [worker_name.get_text() for worker_name in elements]

    return workers_names

def schedule_of_classes(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content= response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        rows = soup.find_all('tr')

        with open('Schedule_of_classes.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)

            for row in rows:
                columns = row.find_all('td')
                row_data = [column.get_text(strip=True) for column in columns]
                csv_writer.writerow(row_data)
                
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

#all urls
url_faculty = 'https://lti.cs.cmu.edu/directory/all/154/1'
url_affiliated_faculty = 'https://lti.cs.cmu.edu/directory/all/154/2728'
url_adjunct_faculty = 'https://lti.cs.cmu.edu/directory/all/154/200'
url_schedule_of_classes = 'https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_spring.htm'


#This will make a csv file of with the timetable of the classes
schedule_of_classes(url_schedule_of_classes)


