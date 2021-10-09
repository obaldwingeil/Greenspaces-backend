from server import mysql_db, Location, User, Image
import peewee as pw

for location in Location.select():
    print(location.name + ': ' + str(location.location_id))
    for image in Image.select().where(Image.location_id == location.location_id):
        print('\t' + image.url)
'''
for user in User.select():
    print(user.name + ': ' + str(user.user_id))'''
