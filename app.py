#!/usr/bin/python
# -*- coding: utf-8 -*-

from application import app, db
from flask import render_template, request, Markup, json, jsonify, \
    Response, redirect, flash, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime, date
import bson
import math
import os.path
import random
from application.forms import ChangePassword, LoginForm, RegisterForm, \
    EditUser, AddNewBook, EditBook, DeleteBook
from werkzeug.security import generate_password_hash, \
    check_password_hash
from werkzeug.utils import secure_filename
from application.models import Users, Books, Categories
from application.dbmodels import Slug, Helper



# All root fundtions are here
# ==========================================================
        # This root for Home Page
# ==========================================================
@app.route('/')
def home():
    page_data = PageData
    return render_template('index.html', class_active='home',page_data=page_data,slug_ob=Slug,recent_books=page_data.get_recent_books(),most_viewed_books=page_data.get_most_viewed_books())

# ==========================================================
        # this root for 404 page excepttion root
# ==========================================================

@app.errorhandler(404)
def not_found(e):
    page_data = PageData()
    return render_template('404.html', page_data=page_data, text=e)

# ==========================================================
        # this root for all category page content
# ==========================================================
@app.route('/category', methods=['GET', 'POST'])
@app.route('/category/<category_slug>/', methods=['GET', 'POST'])
@app.route('/category/<category_slug>/<slug>', methods=['GET', 'POST'])
def category(category_slug='allcategories',slug="page-1"):
    page_data       = PageData
    category_books  = page_data.get_category_books(category_slug)

    if category_books:
        title = Slug.getTitle(category_slug)
    else:
        title =Slug.getTitle(category_slug)
        if category_slug    ==  'most_viewed': title    = 'Most Viewed'
        if category_slug    ==  'recently_added': title = 'Recently Added'
        if category_slug    ==  'allcategories': title  = 'All Categories'

        if category_slug    ==  'recently_added': category_books    = page_data.get_recent_books()
        if category_slug    ==  'most_viewed': category_books       = page_data.get_most_viewed_books()

    books_array = category_books
    books = page_data.get_filter_books(books_array,6,slug)
    pagination_box = page_data.get_pagination_box(books_array.count(),6, url_for('category')+'/'+category_slug+'/',slug)
    return render_template('category.html', slug_ob=Slug, title=title, category_books_array=books, page_data=page_data,pagination_box=pagination_box)

# ==========================================================
        # this root for browse all books
# ==========================================================
@app.route('/browse/', methods=['GET', 'POST'])
@app.route('/browse/<slug>', methods=['GET', 'POST'])
def browse(slug='page-1'):
    page_data       = PageData
    books_array     = page_data.get_recent_books()
    books           = page_data.get_filter_books(books_array,6,slug)
    pagination_box  = page_data.get_pagination_box(books_array.count(),6, url_for('browse'),slug)
    return render_template('browse.html', books=books, class_active='browse', slug_ob=Slug, title='All Books', page_data=page_data, pagination_box=pagination_box)

# ==========================================================
        # this root for single book view
# ==========================================================
@app.route('/book/', methods=['GET', 'POST'])
@app.route('/book/<slug>', methods=['GET', 'POST'])
def book(slug=''):
    page_data   = PageData
    single_book = page_data.get_single_book(slug).first()
    update_view(slug=slug)
    return render_template('single.html', helper=Helper, slug_ob=Slug, book=single_book, page_data=page_data)

# ==========================================================
        # This root for user account controll like profile, My books, Add New book,
        # Change Password, Delete Book, Edit Book
# ==========================================================
@app.route('/account/', methods=['GET', 'POST'])
@app.route('/account/<term>', methods=['GET', 'POST'])
@app.route('/account/<term>/<slug>', methods=['GET', 'POST'])
def account(term='login', slug=''):
    page_data = PageData
    if page_data.check_login():
        active_user     = Users.objects(user_id=session.get('user_id')).first()
        books           = Books.objects(user_id=session.get('user_id')).order_by('-date')
        user            = page_data.get_user_details(session.get('user_id'))
        # this root for user profile
        if term == 'profile':
            return render_template('account/profile.html', user=user, page_data=page_data)
        # this root for user edit profile information like name and email
        elif term == 'edit_profile':
            form = EditUser()
            if form.validate_on_submit():
                name    = form.name.data
                email   = form.email.data
                if user.email == email:
                    user = Users.objects(user_id=session.get('user_id')).update(name=name, email=email)
                    flash('You are successfully updated your profile!', 'success')
                    return redirect(url_for('account') + '/edit_profile')
                else:
                    count = Users.objects(email=email).count()
                    if count > 0:
                        flash('This email already existed! Please try another one.', 'danger')
                        return redirect(url_for('account') + '/edit_profile')
                    else:
                        user = Users.objects(user_id=session.get('user_id')).update(name=name, email=email)
                        flash('You are successfully update your profile!', 'success')
                        return redirect(url_for('account') + '/edit_profile')
            else:
                return render_template('account/edit_profile.html', page_data=page_data,user=user,form=form)
        # this root for user uploaded all books
        elif term == 'books':
            return render_template('account/my_books.html', slug_ob=Slug, user=user, page_data=page_data)
        # this root for user single book view
        elif term == 'view':
            book = page_data.get_single_book(slug).first()
            return render_template('account/view.html', helper=Helper, form=DeleteBook() , user=user, page_data=page_data, single_book=book)
        # this root for user can upload new book
        elif term == 'add_new_book':
            form = AddNewBook()
            if form.validate_on_submit():

                # form upload image file details

                form_file_upload = request.files['upload']
                upload_file_name = str(active_user.user_id) + '_' \
                    + str(random.randint(10, 200)) + '_' \
                    + secure_filename(form_file_upload.filename)
                form_file_upload.save('application/static/uploads/2020/' + upload_file_name)

                book_name   = form.book_name.data
                author      = form.author.data
                user_id     = user.user_id
                image_url   = upload_file_name
                slug        = Slug.getSlug(form.book_name.data)
                ISBN        = form.ISBN.data
                category    = form.category.data
                overview    = form.overview.data
                date        = datetime.now()

                book = Books(
                    book_name   = book_name,
                    author      = author,
                    user_id     = user_id,
                    image_url   = image_url,
                    slug        = slug,
                    ISBN        = ISBN,
                    category    = category,
                    overview    = overview,
                    date        = date,
                    )
                book.save()
                flash('You are successfully added a new book!',
                      'success')
                return redirect(url_for('account') + '/books')
            else:

                return render_template('account/add_new_book.html',
                        page_data=page_data, form=form,user=user)
        # this root for user can edit single bokk information
        elif term == 'edit_book':

            book = page_data.get_single_book(slug).first()
            form = EditBook(request.form, category=book.category)
            print(book)
            if slug:
                if form.validate_on_submit():
                    image_url_link          = book.image_url
                    if request.files['upload']:
                        form_file_upload    = request.files['upload']
                        image_url_link      = str(user.user_id) + '_' + str(random.randint(10, 200)) + '_' \
                            + secure_filename(form_file_upload.filename)
                        if book.image_url: os.remove('application/static/uploads/2020/' + book.image_url)
                        form_file_upload.save('application/static/uploads/2020/' + image_url_link)

                    book_name   = form.book_name.data
                    author      = form.author.data
                    user_id     = user.user_id
                    image_url   = image_url_link
                    slug        = book.slug
                    ISBN        = form.ISBN.data
                    category    = form.category.data
                    overview    = form.overview.data
                    date        = datetime.now()
                    update_book = book.update(
                        book_name   = book_name,
                        author      = author,
                        user_id     = user_id,
                        image_url   = image_url,
                        slug        = slug,
                        ISBN        = ISBN,
                        category    = category,
                        overview    = overview,
                        date        = date,
                        )
                    flash('You are successfully update your book!',
                          'success')
                    return redirect(url_for('account') + 'edit_book/'
                                     + book.slug)
                else:
                    return render_template('account/edit_book.html',
                            page_data=page_data,user=user,form=form, single_book=book)
            else:
                redirect(url_for('account') + 'mybooks')
        # this root for user can delete book information and image as well form database and server
        elif term == 'delete_book':
            form = DeleteBook()
            if slug:
                book = Books.objects(slug=slug)
                os.remove('application/static/uploads/2020/'
                          + book[0].image_url)
                if form.validate_on_submit():
                    book.delete()
                    flash('You\'r book successfully deleted!', 'success'
                          )
                    return redirect(url_for('account') + '/mybooks')
                else:
                    return redirect(url_for('account') + '/book_view/'
                                     + title)
            else:
                return redirect(url_for('account') + '/mybooks')
        # this root for user can change their password
        elif term == 'change_password':
            form = ChangePassword()
            if form.validate_on_submit():
                new_password = form.new_password.data
                active_user.set_password(new_password)
                update_book = \
                    active_user.update(password=active_user.password)
                flash('You\'r password successfully updated!', 'success'
                      )
                return redirect(url_for('account')
                                + '/change_password')
            else:
                return render_template('account/change_password.html'
                        , page_data=page_data,user=user,form=form)
        # this root for user can logout
        elif term == 'logout':
            session['user_id'] = False
            session['login'] = False
            flash('You are successfully logout!', 'danger')
            return redirect(url_for('account') + '/login')
        else:
            return redirect(url_for('account') + '/profile')
    else:
        # this root for new user can register for this webiste
        if term == 'register':
            form = RegisterForm()
            if form.validate_on_submit():
                name = form.name.data
                email = form.email.data
                password = form.password.data
                user = Users.objects(email=email).first()
                if user:
                    flash('You\'r email already existed! Please try another one.'
                          , 'danger')
                    return render_template('account/register.html',
                            page_data=page_data, form=form)
                else:
                    user_id = Users.objects.all().count()
                    user_id += 1
                    name = form.name.data
                    email = form.email.data
                    password = form.password.data

                    user = Users(user_id=user_id, name=name,
                                 email=email, password=password)
                    user.set_password(password)
                    user.save()

                    session['user_id'] = user_id
                    session['login'] = True
                    flash('You are successfully register!', 'success')
                    return redirect(url_for('account') + '/profile')
            else:

                return render_template('account/register.html',
                        page_data=page_data, form=form)
        # this root for user can login
        elif term == 'login':
            form = LoginForm()
            page_data = PageData
            if form.validate_on_submit():
                email = form.email.data
                password = form.password.data
                user = Users.objects(email=email).first()
                if user and user.get_password(password):
                    session['user_id'] = user.user_id
                    session['login'] = True

                    flash('You are successfully logged in!', 'success')
                    return redirect(url_for('account') + '/profile')
                else:
                    if user and user.password != password:
                        flash('Sorry, Email and password didn\'t match! Please try again'
                              , 'danger')
                    else:
                        flash('Sorry, Invalid users details!', 'danger')
                        return redirect(url_for('account')
                                + '/profile')

            return render_template('account/login.html', form=form,
                                   page_data=page_data)
        else:
            return redirect(url_for('account') + '/login')

# All functions or methods are here

# ==========================================================
        # this class controll page data
# ==========================================================

class PageData():
    # check for user login and return true and false
    @staticmethod
    def check_login():
        if session.get('login'):
            return True
        else:
            return False
    # return most recently added books order by date
    def get_recent_books():
        return Books.objects().order_by('-date')

    # return most Viewed added books order by date
    def get_most_viewed_books():
        return Books.objects().order_by('-view')

    # return if user login
    def get_user_details(user_id):
        return Users.objects(user_id=user_id).first()

    # return all category books name
    def get_categories():
        return Categories.objects.all()

    # return category books
    def get_category_books(slug):
        return Books.objects(category=Slug.getTitle(slug))

    # return single book details
    def get_single_book(slug):
        return Books.objects(slug=slug)

    # return user books
    def get_user_books():
        return Books.objects(user_id=session.get('user_id'
                )).order_by('-date')

    def get_pagination_box(total_books, item_number, url, slug):
        pagination_box      = ''
        if total_books > item_number:
            pagination_box  = Markup('<ul class="pagination">')
            result          = math.floor(total_books / item_number)
            reminder        = total_books % item_number
            page_number = 0
            if result > 0 and reminder > 0:
                page_number = result + 1
            elif result > 0 and reminder == 0:
                page_number = result
            for value in range(0, page_number):
                active_page     = ''
                disabled        = ''
                page_id_link = 'page-'+str(value+1)
                if slug == page_id_link:
                    active_page = 'active'
                    disabled    = 'disabled'

                pagination_box += Markup('<li><a href="' + url
                        +  page_id_link + '" ' + disabled + ' class="'
                        + active_page + ' ' + disabled + '">' + str(value + 1)
                        + '</a></li>')

            pagination_box += Markup('</ul>')

            return pagination_box

    def get_filter_books(books, items, slug):
        slug_array      = slug.split('-')
        filter_books    = ''
        if int(slug_array[1])>1:
            filter_books = books[(int(slug_array[1])-1)*items:int(slug_array[1])*items]
        else:
            filter_books = books[0:items]

        return filter_books

# ==========================================================
        # this function for update book view count and update database
# ==========================================================
def update_view(slug):
    book = Books.objects(slug=slug).first()
    book = book.update(
        book_name       = book.book_name,
        author          = book.author,
        user_id         = book.user_id,
        image_url       = book.image_url,
        slug            = book.slug,
        ISBN            = book.ISBN,
        category        = book.category,
        view            = book.view + 1,
        overview        = book.overview,
        date            = book.date,
        )
    return book


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT'
            )), debug=True)
