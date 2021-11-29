from server import Location, User, Image
import peewee as pw
import geojson

'''
test_location = Location.create(
    location_id=1,
    name='test location uploaded from python orm',
)

test_location.save()
'''


def post_data(array):
    '''locations = []
    for location in Location.select():
        locations.append(location.name)'''

    images = []
    for image in Image.select():
        images.append(image.url)

    for location in array[0]:
        # if location['name'] not in locations:
        Location.create(**location)

    for image in array[1]:
        print(image['url'])
        if image['url'] not in images:
            Image.create(**image)


def post_la_parks():
    import laparks_scraper

    # post_data(laparks_scraper.get_lakes_beaches())

    # post_data(laparks_scraper.get_easy_data('pool', "https://www.laparks.org/aquatic/summer-pool"))

    # post_data(laparks_scraper.get_easy_data('dog park', "https://www.laparks.org/dogparks"))

    # post_data(laparks_scraper.get_easy_data('garden', "https://www.laparks.org/horticulture"))

    # post_data(laparks_scraper.check_location_universally_accessible(laparks_scraper.get_easy_data('city park', "https://www.laparks.org/parks")))


def post_la_golf():
    import lacity_golf_scraper
    post_data(lacity_golf_scraper.get_golf_courses())


def post_national_parks():
    import national_parks_api
    # post_data(national_parks_api.get_national_parks())
    post_data(national_parks_api.get_campgrounds())


def add_lat_lon():
    with open('locations.geojson') as f:
        gj = geojson.load(f)
        features = gj['features']
        for feature in features:
            lat_lon = {Location.lat: feature['geometry']['coordinates'][1], Location.long: feature['geometry']['coordinates'][0]}
            query = Location.update(lat_lon).where(Location.location_id == feature['properties']['location_id'])
            query.execute()


if __name__ == "__main__":
    # post_la_parks()
    # post_la_golf()
    # post_national_parks()
    add_lat_lon()
