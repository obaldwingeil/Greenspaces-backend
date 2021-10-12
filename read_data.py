from server import mysql_db, Location, User, Image
import peewee as pw

'''for location in Location.select():
    print(location.name + ': ' + str(location.location_id))
    for image in Image.select().where(Image.location_id == location.location_id):
        print('\t' + image.url)

for user in User.select():
    print(user.name + ': ' + str(user.user_id))

for image in Image.select().where(Image.url == 'https://www.laparks.org/sites/default/files/facility/105th-street-pocket-park/images/105th1.jpg'):
    print(image.location_id)

for image in Image.select():
    print(str(image.location_id) + ': ' + image.url)
    for location in Location.select().where(Location.location_id == image.location_id):
        print(location.name)'''

for location in Location.select().where(Location.type == 'campground'):
    print(location.name + ': ' + str(location.location_id))
    for image in Image.select().where(Image.location_id == location.location_id):
        print('\t' + image.url)