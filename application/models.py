from application import db
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
import sys
from datetime import datetime
from wtforms.fields.html5 import DateField, DateTimeField

# this class mainly connected with users database table controll
class Users(db.Document):
    user_id     = db.IntField(unique=True)
    name        = db.StringField(max_length=50)
    email       = db.StringField(unique=True, max_length=50)
    password    = db.StringField()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

# this class mainly connected with Books database table controll
class Books(db.Document):
    book_name   = db.StringField(max_length=200)
    author      = db.StringField(max_length=200)
    user_id     = db.IntField()
    image_url   = db.StringField()
    slug        = db.StringField()
    ISBN        = db.StringField(max_length=100)
    category    = db.StringField(max_length=100)
    view        = db.IntField(default=1)
    overview    = db.StringField()
    url         = db.StringField()
    date        = db.DateTimeField(default=datetime.now())

    def get_date(self, date):
        self.date   =   date
        date        =   self.date
        final_date  =   str(date.day)
        final_date  += '-'+str(date.strftime("%b"))
        final_date  += ' '+str(date.year)
        #calendar.timegm(time.gmtime())
        return final_date


# this class mainly connected with categories database table controll
class Categories(db.Document):
    category_name = db.StringField(max_length=100)
