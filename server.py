from peewee import Model, IntegerField, TextField, MySQLDatabase

mysql_db = MySQLDatabase('green_spaces', user='root', password='My122096!!', host='localhost', port=3306)


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
    password = TextField(null=True)

    class Meta:
        table_name = 'users'


mysql_db.connect()
