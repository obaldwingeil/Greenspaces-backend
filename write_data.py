from server import Location, User, Image
import peewee as pw

'''
test_location = Location.create(
    location_id=1,
    name='test location uploaded from python orm',
)

test_location.save()
'''


def post_data(array):
    for location in array[0]:
        print(location['location_id'])
        Location.create(**location)

    for image in array[1]:
        Image.create(**image)


def post_la_parks():
    import laparks_scraper

    # post_data(laparks_scraper.get_lakes_beaches())

    # post_data(laparks_scraper.get_easy_data('pool', "https://www.laparks.org/aquatic/summer-pool"))

    # post_data(laparks_scraper.get_easy_data('dog park', "https://www.laparks.org/dogparks"))

    # post_data(laparks_scraper.get_easy_data('garden', "https://www.laparks.org/horticulture"))

    # post_data(laparks_scraper.check_location_universally_accessible(laparks_scraper.get_easy_data('city park', "https://www.laparks.org/parks")))


if __name__ == "__main__":
    post_la_parks()
