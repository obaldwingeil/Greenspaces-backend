from playhouse.shortcuts import model_to_dict

from server import mysql_db, Location, User, Image
from flask import Flask, jsonify, request

# Methods for testing data inserting
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
        print(location.name)

for location in Location.select().where(Location.type == 'campground'):
    print(location.name + ': ' + str(location.location_id))
    for image in Image.select().where(Image.location_id == location.location_id):
        print('\t' + image.url)'''


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/api/locations', methods=['GET'])
def location_endpoint():
    query = Location.select()
    data = [model_to_dict(i) for i in query]

    if data:
        res = jsonify({
            'locations': data,
            'meta': {
                'page_url': request.url,
                'item_count': len(data)
            }
        })
        res.status_code = 200
    else:
        output = {
            "error": "No results found.",
            "url": request.url
        }
        res = jsonify(output)
        res.status_code = 404
    return res


@app.route('/api/images/<int:location_id>', methods=['GET'])
def image_by_location_endpoint(location_id):
    query = Image.select().where(Image.location_id == location_id)
    data = [model_to_dict(i) for i in query]

    if data:
        res = jsonify({
            'images': data,
            'meta': {
                'page_url': request.url,
                'item_count': len(data),
            }
        })
        res.status_code = 200
    else:
        output = {
            "error": "No results found.",
            "url": request.url
        }
        res = jsonify(output)
        res.status_code = 404
    return res


if __name__ == '__main__':
    app.run()
