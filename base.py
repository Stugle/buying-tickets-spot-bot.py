import datetime
from peewee import *

db = SqliteDatabase('tiket.db')



class Standard(Model):
    nomer = PrimaryKeyField(unique=True)
    name = CharField()
    price = IntegerField()
    who = CharField()
    empty = BooleanField()
    whom = CharField()
    class Meta:
        database = db
        order_by = "nomer"

class Vip(Model):
    nomer = PrimaryKeyField(unique=True)
    name = CharField()
    price = IntegerField()
    who = CharField()
    empty = BooleanField()
    whom = CharField()
    class Meta:
        database = db
        order_by = "nomer"

class Buyer(Model):
    nomer = PrimaryKeyField(unique=True)
    whom = CharField()
    who = CharField()
    place = CharField()
    owner = CharField()
    card = IntegerField()
    cvc = IntegerField()
    price = IntegerField()
    time = DateTimeField(default=datetime.datetime.now)
    button = IntegerField()
    type_db = BooleanField()
    type_button = BooleanField()
    class Meta:
        database = db
        order_by = "nomer"


