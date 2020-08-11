import os
from flask import Flask, render_template, request, json, jsonify, Response, redirect, flash, url_for, session
from flask import render_template, request, json, jsonify, Response, redirect, flash, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime
import time
import bson
import calendar
#from application.models import Users, Books, Testuser
"""
This file mainly helper method for app file and html file.
# slug making and get slug
# get date
# get all categories

"""
class Allcategory():
    app1 = Flask(__name__)
    app1.config['MONGO_DBNAME']='book_shop'
    app1.config['MONGO_URI'] = 'mongodb+srv://root:Zee9Zee9@firstcluster.qhtcj.mongodb.net/book_shop?retryWrites=true&w=majority'

    app1.secret_key = 'asdfaiueh345345wk3jfnsdjkfkdjfvkdfjgsdfg45345'

    mongo1 = PyMongo(app1)
    categories=mongo1.db.categories.find()
    final_category=[]
    #final_category.append('Select Your Category')
    for category in categories:
        final_category.append(category['category_name'])

    def getFinalCategory():
        app1 = Flask(__name__)
        app1.config['MONGO_DBNAME']='book_shop'
        app1.config['MONGO_URI'] = 'mongodb+srv://root:Zee9Zee9@firstcluster.qhtcj.mongodb.net/book_shop?retryWrites=true&w=majority'

        app1.secret_key = 'asdfaiueh345345wk3jfnsdjkfkdjfvkdfjgsdfg45345'

        mongo1 = PyMongo(app1)
        categories=mongo1.db.categories.find()
        final_category=[]
        final_category.append(['Select Your Category','Select Your Category'])
        for category in categories:
            final_category.append([category['category_name'],category['category_name']])
        return final_category

    #test=final_category[0]


class Slug():

    def getUrlTitle(title):
        final_title = title.split()
        final_title = "-".join(final_title)
        return final_title.lower()

    def getTitle(url_title):
        final_title = url_title.rsplit("-")
        final_title = " ".join(final_title)
        return final_title.title()

    def getBookTitle(book_title):
        if len(book_title)>15:
            return book_title[0:14]+'..'
        else:
            return book_title

    def getSlug(title):
        final_title = title.split()
        final_title = "-".join(final_title)
        now = datetime.now()
        return final_title.lower()+'-'+now.strftime("%Y-%m-%d-%H-%M-%S")



class Helper():

    def getDate(timestamp):
        date=timestamp
        final_date = str(date.day)
        final_date += '-'+str(date.strftime("%b"))
        final_date += ' '+str(date.year)
        #final_date += ' '+str(date.strftime("%H:%M:%S"))
        #calendar.timegm(time.gmtime())
        return final_date

    def getTimestamp(datetime_str):
        datetime_object = datetime.strptime(datetime_str, '%m/%d/%y')
        return datetime_object
