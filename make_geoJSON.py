from server import mysql_db, Location
from geojson import Point, Feature, FeatureCollection, dump

from requests import get
features = []


for location in Location.select():
    print(location.name)
    address = location.address.replace(' ', '+')
    api_response = get("https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyBzKDIyZNbBILmkac1oBvu4iTJqPj4vdOU".format(address=address)).json()
    print(api_response['results'][0]['geometry'])
    geometry = api_response['results'][0]['geometry']
    if 'location' in geometry:
        point = Point((geometry['location']['lng'], geometry['location']['lat']))
    else:
        point = Point((geometry['bounds']['northeast']['lng'], geometry['bounds']['northeast']['lat']))
    properties = {
        "type": location.type,
        "location_id": str(location.location_id),
        "name": location.name,
        "description": location.description,
        "rating": location.rating
    }
    features.append(Feature(geometry=point, properties=properties))
print(len(features))

with open('locations.geojson', 'w') as f:
    feature_collection = FeatureCollection(features)
    dump(feature_collection, f)
