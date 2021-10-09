from requests import get
from contextlib import closing
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
import uuid
from copy import deepcopy


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as response:
            if is_good_response(response):
                return response.content
            else:
                return None

    except RequestException as e:
        print("Error: cannot get the url")
        return None


def is_good_response(response):
    content_type = response.headers["Content-Type"].lower()

    return (response.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def get_easy_data(location_type, url):
    locations = []
    images = []
    raw_html = simple_get(url)
    if raw_html is not None:
        page_content = BeautifulSoup(raw_html, "html.parser")
        table = page_content.find("table")
        for row in table.select("tr"):
            location = {}
            for name in row.findAll('a'):
                location['name'] = name.text
                location['link'] = "https://www.laparks.org" + name['href']
            for address in row.findAll('td', {'class': 'views-field-field-address'}):
                location['address'] = re.sub('\s+', ' ', address.text).strip()
            if location:
                location['location_id'] = uuid.uuid1().int >> 64
                location['type'] = location_type
                locations.append(location)

        for location in locations:
            item_html = simple_get(location['link'])
            if item_html is not None:
                item_content = BeautifulSoup(item_html, "html.parser")
                fields = item_content.findAll('div', {'class': 'field'})
                activities = ""
                for field in fields:
                    # print(field.text)
                    text = field.text.replace(u'\xa0', u' ').replace('\n', ' ')
                    # add email
                    if 'Email' in field.text:
                        location['email'] = text[text.index(':') + 2:]
                    # add activities
                    if 'Programs' in field.text:
                        activities += text[text.index(':') + 2:]
                    # add description
                    if 'Facility Features' in field.text:
                        location['features'] = re.sub('\s+', ' ', field.text).strip().replace('Facility Features ', '')
                    # add hours
                    if 'Hours' in field.text:
                        location['hours'] = text[text.index(':') + 2:]
                    # add phone
                    if 'Phone' in field.text:
                        while ':' in text:
                            text = text[text.index(':') + 2:]
                        if 'phone' not in location:
                            location['phone'] = text
                if len(activities) != 0:
                    location['activities'] = activities
                # print(location)
                # get images
                for image in item_content.findAll('a', {'class': 'colorbox'}):
                    images.append({'url': image['href'], 'location_id': location['location_id']})
                # print(images)
        return [locations, images]


def get_lakes_beaches():
    locations = []
    images = []
    location_names = []
    raw_html = simple_get("https://www.laparks.org/aquatic/lakes-fishing-beaches")
    if raw_html is not None:
        page_content = BeautifulSoup(raw_html, "html.parser")
        tables = page_content.findAll('table')
        for table in tables:
            if 'Symbol Key' not in table.find("tr", {'class': 'bg-primary'}).text:
                beach = 'Beaches' in table.find("tr", {'class': 'bg-primary'}).text
                for row in table.select("tr"):
                    if not row.has_attr('class') or 'warning' in row['class']:
                        location = {}
                        if '(S)' in row.text:
                            location['seasonal'] = 'Seasonal'
                        elif '(YR)' in row.text:
                            location['seasonal'] = 'Year Round'
                        elif '(WYR)' in row.text:
                            location['seasonal'] = 'Weekend Year Round'
                        for name in row.findAll('a'):
                            location['name'] = name.text
                            location['link'] = "https://www.laparks.org" + name['href']
                        location['address'] = row.text.split('\n')[2]
                        if location:
                            if beach:
                                location['type'] = 'beach'
                            else:
                                location['type'] = 'open water facility'
                            location['location_id'] = uuid.uuid1().int >> 64
                            if location['name'] not in location_names:
                                locations.append(location)
                            location_names.append(location['name'])
                        # print(location)
        for location in locations:
            water_html = simple_get(location['link'])
            if water_html is not None:
                water_content = BeautifulSoup(water_html, "html.parser")
                fields = water_content.findAll('div', {'class': 'field'})
                activities = ""
                for field in fields:
                    # print(field.text)
                    # add phone
                    text = field.text.replace(u'\xa0', u' ').replace('\n', ', ')
                    if 'Phone' in field.text:
                        location['phone'] = text[text.index(':') + 2:]
                    # add email
                    if 'Email' in field.text:
                        location['email'] = text[text.index(':') + 2:]
                    # add activities
                    if 'Programs' in field.text:
                        activities += text[text.index(':') + 2:]
                    # add description
                    if 'Facility Features' in field.text:
                        location['features'] = re.sub('\s+', ' ', field.text).strip().replace('Facility Features ', '')
                    if 'Hours' in field.text:
                        if location['name'] == 'Hansen Dam Aquatic Center':
                            location['hours'] = '7:30am - 6:00pm (Recreational Lake Only)'
                        elif 'hours' not in location:
                            location['hours'] = text[text.index(':') + 2:]
                if len(activities) != 0:
                    location['activities'] = activities
                # print(location)
                # get images
                for image in water_content.findAll('a', {'class': 'colorbox'}):
                    images.append({'url': image['href'], 'location_id': location['location_id']})
                # print(images)
        return [locations, images]


def check_location_universally_accessible(total_locations):
    uap_locations = []
    raw_html = simple_get("https://www.laparks.org/uap")
    if raw_html is not None:
        page_content = BeautifulSoup(raw_html, "html.parser")
        table = page_content.find("table")
        for row in table.select("tr"):
            for name in row.findAll('a'):
                uap_locations.append(name.text)
        for location in total_locations[0]:
            if location['name'] in uap_locations:
                location['accessibility'] = 'universally accessible playground'
                # print(location)
        return total_locations

