from peewee import Model, IntegerField, TextField, MySQLDatabase, DoubleField

mysql_db = MySQLDatabase('green_spaces', user='open', password='Ro122096!!', host='0.0.0.0', port=3306)


class Base(Model):
    class Meta:
        database = mysql_db


class Location(Base):
    location_id = IntegerField(primary_key=True, null=False, index=True)
    name = TextField(null=True)
    address = TextField(null=True)
    link = TextField(null=True)
    activities = TextField(null=True)
    features = TextField(null=True)
    phone = TextField(null=True)
    email = TextField(null=True)
    seasonal = TextField(null=True)
    type = TextField(null=True)
    accessibility_description = TextField(null=True)
    description = TextField(null=True)
    details = TextField(null=True)
    cost = TextField(null=True)
    hours = TextField(null=True)
    weather = TextField(null=True)
    reservations = TextField(null=True)
    rating = DoubleField(null=True)
    lat = DoubleField(null=True)
    long = DoubleField(null=True)

    class Meta:
        table_name = 'locations'


class Image(Base):
    url = TextField(primary_key=True, null=False, index=True)
    location_id = IntegerField(null=True)
    review_id = IntegerField(null=True)
    user_id = IntegerField(null=True)

    class Meta:
        table_name = 'images'


class User(Base):
    user_id = IntegerField(primary_key=True, null=False, index=True)
    name = TextField(null=True)
    email = TextField(null=True)
    locations = TextField(null=True)

    class Meta:
        table_name = 'users'


class Review(Base):
    review_id = IntegerField(primary_key=True, null=False, index=True)
    user_id = IntegerField(null=True)
    location_id = IntegerField(null=True)
    description = IntegerField(null=True)
    rating = DoubleField(null=True)
    user_name = TextField(null=True)
    location_name = TextField(null=True)

    class Meta:
        table_name = 'reviews'


mysql_db.connect()
