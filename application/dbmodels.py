import os
from flask import Flask, render_template, request, json, jsonify, Response, redirect, flash, url_for, session
from flask import render_template, request, json, jsonify, Response, redirect, flash, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime
import time
import bson
import calendar
from application.models import Categories

# Category select form helper for upload book category
class Allcategory():
    categories      =  Categories.objects.all()
    final_category  =  []
    for category in categories:
        final_category.append(category['category_name'])
    def getFinalCategory():
        categories      = Categories.objects.all()
        final_category  = []
        final_category.append(['Select Your Category','Select Your Category'])
        for category in categories:
            final_category.append([category['category_name'],category['category_name']])
        return final_category

    def get_book_category():
        return Books.objects(user_id=session.get('user_id'
            )).order_by('-date')

# page slug helper
class Slug():
    # this method return user friendly slug or url
    def getUrlTitle(title):
        final_title     = title.split()
        final_title     = "-".join(final_title)
        return final_title.lower()

    # this method return slug to display title
    def getTitle(url_title):
        final_title     = url_title.rsplit("-")
        final_title     = " ".join(final_title)
        return final_title.title()

    # this method return long title to short title
    def getBookTitle(book_title):
        if len(book_title)>15:
            return book_title[0:14]+'..'
        else:
            return book_title

    # this method return slug or url with unique slug
    def getSlug(title):
        final_title     = title.split()
        final_title     = "-".join(final_title)
        now             = datetime.now()
        return final_title.lower()+'-'+now.strftime("%Y-%m-%d-%H-%M-%S")


# this is helper class for timestamp
class Helper():

    def getDate(timestamp):
        date        = timestamp
        final_date  = str(date.day)
        final_date  += '-'+str(date.strftime("%b"))
        final_date  += ' '+str(date.year)
        #final_date += ' '+str(date.strftime("%H:%M:%S"))
        #calendar.timegm(time.gmtime())
        return final_date

    def getTimestamp(datetime_str):
        datetime_object = datetime.strptime(datetime_str, '%m/%d/%y')
        return datetime_object
