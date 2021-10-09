import uuid

from requests import get
from contextlib import closing
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re

# data holders to transfer to db
courses = []
images = []


def simple_get(url):
    try:
        with closing(get(url, stream=True, verify=False)) as response:
            if is_good_response(response):
                return response.content
            else:
                return None

    except RequestException as e:
        print(e)
        print("Error: cannot get the url")
        return None


def is_good_response(response):
    content_type = response.headers["Content-Type"].lower()

    return (response.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def clean(text):
    return re.sub('\s+', ' ', text).strip()


def get_golf_courses():
    raw_html = simple_get("http://golf.lacity.org")
    if raw_html is not None:
        page_content = BeautifulSoup(raw_html, "html.parser")
        course_list = page_content.findAll('div', {'class': 'col-md-4'})
        for course in course_list:
            # print(course)
            if course.find('span', {'class': 'dropdown-wide-heading'}) is not None:
                course_type = course.find('span', {'class': 'dropdown-wide-heading'}).text
                for name in course.findAll('a'):
                    location = {
                        'name': name.text,
                        'link': "http://golf.lacity.org" + name['href'],
                        'type': 'golf course',
                        'features': course_type[:len(course_type)-1].replace('\n', '').strip() + ', ',
                        'location_id': uuid.uuid4()
                    }
                    courses.append(location)

        for location in courses:
            item_html = simple_get(location['link'])
            if item_html is not None:
                item_content = BeautifulSoup(item_html, "html.parser")
                course_details = item_content.find('article', {'id': 'course-details'})
                attributes = course_details.findAll('p')
                location['description'] = attributes[0].text.replace('\n', '').replace(u'\xa0', u' ').strip()
                details = ""
                for detail in attributes[1]:
                    if len(detail.text) != 0:
                        details += clean(detail.text) + ', '
                location['details'] = details
                amenities = course_details.find('ul')
                features = ""
                for amenity in amenities.select('li'):
                    features += amenity.text.replace('\n', '').strip().replace(u'\xa0', u' ') + ', '
                location['features'] += features
                fees = item_content.find('article', {'id': 'green-fees'})
                table = fees.find('table')
                cost_array = []
                for row in table.select('tr'):
                    row_list = row.findAll('td')
                    if row_list:
                        if len(row_list) == 3:
                            cost_array.append({
                                'play': clean(row_list[0].text),
                                'weekdays': clean(row_list[1].text),
                                'weekends': clean(row_list[2].text)
                            })
                        else:
                            cost_array.append({
                                'play': clean(row_list[0].text),
                                'weekdays': clean(row_list[1].text),
                            })
                location['cost'] = str(cost_array)
                course_info = item_content.find('aside', {'class': 'col-md-4'})
                info = course_info.find('ul').findAll('li')
                phone = clean(info[0].text)
                location['phone'] = phone[phone.index(':') + 2:]
                for line in info:
                    if 'Email' in line.text:
                        email = clean(line.text)
                        location['email'] = email[email.index(':') + 2:]
                location['address'] = clean(course_info.find('address').text)

                image_html = item_content.findAll('a', {'class': 'image-link'})
                for image in image_html:
                    images.append({'url': "http://golf.lacity.org" + image['href'], 'location_id': location['location_id']})
                    # print(images)

        return [courses, images]
