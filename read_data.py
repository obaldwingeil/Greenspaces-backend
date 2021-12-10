from peewee import NodeList, SQL, fn
from playhouse.shortcuts import model_to_dict

from server import Location, User, Image, Review
from flask import Flask, jsonify, request
import math
import json

allTypes = ["golf course", "city park", "national park", "open water facility", "beach",
            "campground", "pool", "garden", "dog park"]

filterAlts = {
    "universally accessible playground (uap)": ["universally accessible playground"],
    "hiking / jogging trail": ["hiking", "walking", "jogging"],
    "play area / playground": ["children’s play area", "childrens play area", "playground"],
    "toilets": ["restroom", "bathroom", "toilet"],
    "showers": ["shower"],
    "picnic area": ["outdoor tables", "picnic area"],
    "restaurant / cafe": ["restaurant", "cafe", "coffee", "snack"],
    "bike path": ["mountain biking", "bike path"],
    "fishing": ["fishing permitted (yes)", "fishing"],
    "boating / sailing": ["boating", "sailing"],
}


def getFeatures():
    features = []
    for location in Location.select():
        if location.activities:
            for feature in location.activities.split(', '):
                if feature not in features:
                    features.append(feature)


app = Flask(__name__)
app.config.from_object(__name__)


# Get user
@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):

    query = User.select().where(User.user_id == user_id)
    data = [model_to_dict(i) for i in query]

    if data:
        res = jsonify({
            'user': data,
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


# Add saved location to user
@app.route('/api/user/add/<user_id>', methods=['POST'])
def add_user_location(user_id):
    location_id = str(json.loads(request.json['locationId']))
    saved = request.json['saved']

    user = model_to_dict(User.get(user_id=user_id))
    locations = user['locations']
    if saved:
        if locations is None:
            user_query = (User
                          .update({User.locations: (location_id + ", ")})
                          .where(User.user_id == user_id))
        else:
            user_query = (User
                          .update({User.locations: (User.locations + location_id + ", ")})
                          .where(User.user_id == user_id))
        user_query.execute()
    elif locations is not None:
        locations = locations.replace(location_id + ", ", "")
        user_query = (User
                      .update({User.locations: locations})
                      .where(User.user_id == user_id))

        user_query.execute()

    res = jsonify({
        'user_id': user_id,
        'location_id': location_id,
        'saved': saved
    })
    res.status_code = 200
    return res


# Add new user
@app.route('/api/user/addUser', methods=['POST'])
def add_user():
    user_id = json.loads(request.json['userId'])
    user_name = request.json['name']
    user_email = request.json['email']

    user, created = User.get_or_create(
        user_id=user_id,
        email=user_email,
        name=user_name
    )

    res = jsonify({
        'user_email': user.email,
        'user_id': user.user_id,
        'created': created
    })
    res.status_code = 200
    return res


# Get all locations
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


def Match(columns, expr, modifier=None):
    match = fn.MATCH(*columns)  # MATCH(col0, col1, ...)
    args = expr if modifier is None else NodeList((expr, SQL(modifier)))
    return NodeList((match, fn.AGAINST(args)))


# Get filtered locations
@app.route('/api/locations/filtered', methods=['GET'])
def filtered_location_endpoint():
    filter_list = request.json['filterList'].replace("[", "").replace("]", "").split(", ")
    type_list = request.json['typeList'].replace("[", "").replace("]", "").split(", ")
    min_rating = float(json.loads(request.json['minRating']))
    sort_by = request.json['sortBy']
    point = json.loads(request.json['point'])
    search_query = request.json['searchQuery']
    user_id = request.json['userId']
    saved = request.json['saved']

    if len(type_list) == 1 and type_list == ['']:
        type_list = allTypes

    if len(filter_list) == 1 and filter_list == ['']:
        filter_list = []

    user = model_to_dict(User.get(user_id=user_id))
    if user['locations'] is not None:
        saved_locations = user['locations'].split(", ")
    else:
        saved_locations = []

    if len(search_query) != 0 and saved:
        query = Location.select().where(
            (Location.type << type_list) &
            (Location.rating >= min_rating) &
            (Location.location_id << saved_locations) &
            (Match((Location.name, Location.features, Location.activities, Location.description, Location.type), search_query))
        )
    elif len(search_query) != 0:
        query = Location.select().where(
            (Location.type << type_list) &
            (Location.rating >= min_rating) &
            (Match((Location.name, Location.features, Location.activities, Location.description, Location.type), search_query))
        )
    elif saved:
        query = Location.select().where(
            (Location.type << type_list) &
            (Location.rating >= min_rating) &
            (Location.location_id << saved_locations)
        )
    else:
        query = Location.select().where((Location.type << type_list) & (Location.rating >= min_rating))

    data = [model_to_dict(i) for i in query]

    filtered_data = []

    for location in data:
        features = []
        activities = []
        if location["features"]:
            features = location["features"].lower()
        if location["activities"]:
            activities = location["activities"].lower()

        has_features = True
        for feature in filter_list:
            feature = feature.lower()
            if feature not in filterAlts:
                if feature not in features and feature not in activities:
                    has_features = False
            else:
                has_feature = False
                for alt in filterAlts[feature]:
                    if alt in features or alt in activities:
                        if (feature == 'fishing' and 'fishing permitted (no)' in features) or feature != "fishing":
                            has_feature = True
                if not has_feature:
                    has_features = False

        if has_features:
            filtered_data.append(location)

    user = model_to_dict(User.get(user_id=user_id))
    saved_locations = user['locations']

    if filtered_data:
        if sort_by == "Distance":
            sorted_data = sorted(filtered_data, key=lambda item: (distance_sort(item, point)))
        elif sort_by == "Highest Rated":
            sorted_data = sorted(filtered_data, key=lambda item: item["rating"], reverse=True)
        else:  # Alphabetical
            sorted_data = sorted(filtered_data, key=lambda item: item["name"])

        res = jsonify({
            'locations': sorted_data,
            'saved': saved_locations,
            'meta': {
                'page_url': request.url,
                'item_count': len(filtered_data)
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


def distance_sort(location, point):
    return math.pow((location['long']-float(point[1])), 2) + math.pow((location['lat']-float(point[0])), 2)


# Get locations sorted by distance
@app.route('/api/locations/distance', methods=['GET'])
def locations_by_distance():
    point = json.loads(request.json['point'])  # [32,181]
    query = Location.select()
    data = [model_to_dict(i) for i in query]

    if data:
        sorted_data = sorted(data, key=lambda location: (distance_sort(location, point)))

        res = jsonify({
            'locations': sorted_data,
            'meta': {
                'page_url': request.url,
                'item_count': len(data),
                'sorted': 'distance'
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


# Get location by ID
@app.route('/api/locations/<int:location_id>', methods=['GET'])
def location_by_id_endpoint(location_id):
    query = Location.select().where(Location.location_id == location_id)
    data = [model_to_dict(i) for i in query]

    if data:
        res = jsonify({
            'location': data,
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


# Get images for location by ID
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


# Get image and is saved by location ID and user ID
# Get images for location by ID
@app.route('/api/images/<int:location_id>/<user_id>', methods=['GET'])
def image_by_location_saved(location_id, user_id):
    query = Image.select().where(Image.location_id == location_id)
    data = [model_to_dict(i) for i in query]

    user = model_to_dict(User.get(user_id=user_id))
    locations = user['locations']

    if locations is not None:
        saved = str(location_id) in locations
    else:
        saved = False

    location = model_to_dict(Location.get(location_id=location_id))
    rating = location['rating']

    if data:
        res = jsonify({
            'images': data,
            'saved': saved,
            'rating': rating,
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


# Get images by list of location IDs
@app.route('/api/images/location_ids', methods=['GET'])
def images_by_location_id():
    location_ids = json.loads(request.json["location_ids"])
    query = Image.select().where(Image.location_id << location_ids)
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


# Get user images by user or location
@app.route('/api/user_images/<int:_id>', methods=['GET'])
def image_by_location_or_user(_id):
    parent = request.json['parent']

    if parent == 'location':
        query = Image.select().where((Image.location_id == _id) & (Image.user_id.is_null(False)))
    else:
        query = Image.select().where(Image.user_id == _id)

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


# Get images by review ids
@app.route('/api/images/review_ids', methods=['GET'])
def images_by_review_id():
    review_ids = json.loads(request.json["review_ids"])
    query = Image.select().where(Image.review_id << review_ids)
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


# Get reviews for location by ID
@app.route('/api/reviews/<int:location_id>', methods=['GET'])
def review_by_location_endpoint(location_id):
    review_query = Review.select().where(Review.location_id == location_id)
    reviews = [model_to_dict(i) for i in review_query]

    image_query = Image.select().where((Image.location_id == location_id) & (Image.review_id.is_null(False)))
    images = [model_to_dict(i) for i in image_query]

    for review in reviews:
        review['images'] = []
        for image in images:
            if image['review_id'] == review['review_id']:
                review['images'].append(image)

    if reviews:
        res = jsonify({
            'reviews': reviews,
            'meta': {
                'page_url': request.url,
                'item_count': len(reviews),
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


# Get reviews by user ID
@app.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def review_by_user_endpoint(user_id):
    query = Review.select().where(Review.user_id == user_id)
    data = [model_to_dict(i) for i in query]

    if data:
        res = jsonify({
            'reviews': data,
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


# Add new review
@app.route('/api/post_review', methods=['POST'])
def post_review():
    text = request.json['text']
    rating = float(json.loads(request.json['rating']))
    location_id = json.loads(request.json['locationId'])
    location_name = request.json['locationName']
    user_id = json.loads(request.json['userId'])
    user_name = request.json['userName']
    images = request.json['images'].replace("[", "").replace("]", "").split(", ")

    existing = Review.select()
    review_id = len(existing)

    # Add review
    Review.create(
        review_id=review_id,
        description=text,
        rating=rating,
        location_id=location_id,
        location_name=location_name,
        user_id=user_id,
        user_name=user_name,
    )

    # Update Location average
    reviews = Review.select().where(Review.location_id == location_id)
    review_count = len(reviews)
    location_query = (Location
                      .update({Location.rating: (((review_count * Location.rating) + rating) / review_count)})
                      .where(Location.location_id == location_id))
    location_query.execute()

    # Add images
    if images != ['']:
        for image in images:
            Image.create(
                url=image,
                review_id=review_id,
                location_id=location_id,
                user_id=user_id
            )

    res = jsonify({
        'review_id': review_id,
        'image_count': len(images)
    })
    res.status_code = 200
    return res


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)

    ''' TEST for distance_sort()
    test_locations = [
        {'name': 'Walt', 'lat': 34.13050253287363, 'long': -118.21674881960676},
        {'name': 'Muddy Paw', 'lat': 34.128264511422145, 'long': -118.21743546505283},
        {'name': 'Sprouts', 'lat': 34.136363736807176, 'long': -118.21657715824526}]

    test_point = [34.12593743565167, -118.21927507263004]
    print(sorted(test_locations, key=lambda location: distance_sort(location, test_point)))'''

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


