import uuid

from requests import get
from string import Template


def create_address(address_json):
    for address in address_json:
        if address['type'] == 'Physical':
            return Template('$line1, $line2, $line3, $city, $stateCode $postalCode').substitute(address).replace(', , ',
                                                                                                                 '')


def value_check(value):
    return "No" not in value and "None" not in value and "false" not in value


def get_amenities(amenities):
    amenities_str = ""
    for (key, value) in amenities.items():
        if value_check(value):
            if type(value) is list:
                for item in value:
                    if value_check(item):
                        amenities_str += key + ' (' + item.replace('Yes - ', '') + '), '
            else:
                amenities_str += key + ' (' + value.replace('Yes - ', '') + '), '
    return amenities_str


def get_accessibility(accessibility_json):
    accessibility = ""
    for (key, value) in accessibility_json.items():
        if type(value) is list:
            for item in value:
                accessibility += key + ': ' + item + '. '
        elif value == '1':
            accessibility += key + '. '
        elif value != "" and value != '0':
            accessibility += value + ' '
    return accessibility


def get_national_parks():
    national_parks = []
    images = []
    api_response = get("https://developer.nps.gov/api/v1/parks?stateCode=CA&limit=1000&api_key=GPXBhNzPUkbLHnn9h8f4cargTtaCrfkCdhgnX7sr").json()['data']

    for n_park in api_response:
        activities_json = n_park['activities']
        activities = ""
        for activity in activities_json:
            activities += activity['name'] + ", "

        park = {
            'name': n_park['fullName'],
            'address': create_address(n_park['addresses']),
            'link': n_park['url'],
            'activities': activities,
            'phone': n_park['contacts']['phoneNumbers'][0]['phoneNumber'],
            'email': n_park['contacts']['emailAddresses'][0]['emailAddress'],
            'type': 'national park',
            'description': n_park['description'],
            'cost': str([n_park['entranceFees'] + n_park['entrancePasses']]),
            'seasonal': n_park['operatingHours'][0]['description'],
            'hours': ', '.join(': '.join((key,  val)) for (key, val) in n_park['operatingHours'][0]['standardHours'].items()),
            'weather': n_park['weatherInfo'],
            'location_id': uuid.uuid1().int >> 68
        }
        national_parks.append(park)

        for image in n_park['images']:
            image_obj = {'url': image['url'], 'location_id': park['location_id']}
            if image_obj not in images:
                images.append(image_obj)
    return [national_parks, images]


def get_campgrounds():
    campgrounds = []
    images = []
    api_response = get("https://developer.nps.gov/api/v1/campgrounds?stateCode=CA&limit=1000&api_key=GPXBhNzPUkbLHnn9h8f4cargTtaCrfkCdhgnX7sr").json()['data']
    for cg in api_response:
        phone = None
        if len(cg['contacts']['phoneNumbers']) != 0:
            phone = cg['contacts']['phoneNumbers'][0]['phoneNumber']

        email = None
        if len(cg['contacts']['emailAddresses']) != 0:
            email = cg['contacts']['emailAddresses'][0]['emailAddress']

        hours = None
        seasonal = None
        if len(cg['operatingHours']) != 0:
            seasonal = cg['operatingHours'][0]['description']
            hours = ', '.join(': '.join((key, val)) for (key, val) in cg['operatingHours'][0]['standardHours'].items())

        campground = {
            'name': cg['name'],
            'address': create_address(cg['addresses']),
            'link': cg['url'],
            'features': get_amenities(cg['amenities']),
            'phone': phone,
            'email': email,
            'type': 'campground',
            'description': cg['description'],
            'reservation': cg['reservationInfo'],
            'cost': str(cg['fees']),
            'seasonal': seasonal,
            'hours': hours,
            'weather': cg['weatherOverview'].replace('<a href="', 'weather forecast: ').replace('</a>', '').replace('">weather forecast', ''),
            'location_id': uuid.uuid1().int >> 68,
            'accessibility': get_accessibility(cg['accessibility']),

        }
        campgrounds.append(campground)

        for image in cg['images']:
            image_obj = {'url': image['url'], 'location_id': campground['location_id']}
            if image_obj not in images:
                images.append(image_obj)

    return [campgrounds, images]

