
from application import app, db
from flask import render_template, request, Markup, json, jsonify, Response, redirect, flash, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime, date
import bson, math
import os.path
import random
from application.forms import ChangePassword, LoginForm, RegisterForm, EditUser, AddNewBook, EditBook, DeleteBook
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from application.models import Users, Books, Testuser, Categories
from application.dbmodels import Slug, Helper
#from flask_uploads import configure_uploads, IMAGES, UploadSet



def check_login():
    if session.get('login'):
        return True
    else:
        return False
# page not found direction
@app.route('/page_not_found')
def page_not_found():
    login=check_login()
    return render_template('404.html', login=login)




@app.route('/')
def home():
    page_data = page_initial_data('home', None, None)

    return render_template('index.html', page_data=page_data)
    #return render_template('index.html', login=login, categories=mongo.db.categories.find(), categories1=mongo.db.categories.find())

def pagination(count,range_product,magic_number,page_link):
    magic_number=magic_number
    if count>magic_number:
        range_array=range_product.split('-')
        pagination_block=Markup('<ul class="pagination">')
        result = math.floor(count/magic_number)
        reminder = count%magic_number
        page_number=0
        if result>0 and reminder>0:
            page_number = result+1
        elif result>0 and reminder==0:
            page_number = result
        for value in range(0,page_number):
            active=''
            disabled=''
            items=str((value*magic_number+1))+'-'+str((magic_number*(value+1)))
            if (value*magic_number+1)==int(range_array[0]):
                active='active'
                disabled='disabled'

            pagination_block+=Markup('<li><a href="'+page_link+'/?items='+items+'" '+disabled+' class="'+active+' '+disabled+'">'+str(value+1)+'</a></li>')

        pagination_block+=Markup('</ul>')
        #return math.floor(count/magic_number)
        return pagination_block
    else:
        return ''

magic_number=6

def get_pagination(books,items,page_link):
    range_product='1-'+str(magic_number)
    filter_books=''
    if items:
        range_product=items
        range_array=range_product.split('-')
        filter_books = books[(int(range_array[0])-1):(int(range_array[1]))]
    else:
        filter_books = books[0:magic_number]

    return [pagination(books.count(),range_product,magic_number,page_link),filter_books]

def update_view(slug):
    book = Books.objects(slug=slug)
    book = book.update(book_name=book[0].book_name, author=book[0].author, user_id=book[0].user_id, image_url=book[0].image_url, slug=book[0].slug, ISBN=book[0].ISBN, category=book[0].category, view=(book[0].view+1), overview=book[0].overview, date=book[0].date)
    return book

def is_books_content(books_content):
    if books_content:
        return  True
    else:
        return  False

def page_initial_data(content,slug,term):
    class PageData():
        login           = check_login()
        categories      = Categories.objects.all()
        recently_added  = Books.objects().order_by('-date')
        most_viewed     = Books.objects().order_by('-view')
        slug_ob         = Slug
        user            = ''
        user_books      = ''
        helper          = Helper
        initial_books   = ''
        books_content   = False
        form            = ''
        if content == 'home':
            initial_books   = recently_added
            books_content   = True
        if content == 'browse':
            page_title      = 'All Books'
            initial_books   = recently_added
            books_content   = True

        if content == 'category' and slug:
            if slug == 'allcategories':
                books_content   = False
                page_title      = 'All Categories'
                initial_books   = categories
            elif slug=='recently_added':
                books_content   = True
                page_title      = 'Recently Added'
                initial_books   = recently_added
            elif slug=='most_viewed':
                books_content   = True
                page_title      = 'Most Viewed'
                initial_books   = most_viewed
            else:
                books_content   = True
                initial_books   = Books.objects(category=slug_ob.getTitle(slug))
                page_title      = slug_ob.getTitle(slug)+' Books'
        if content == 'single_book':
            if slug:
                books_content   = True
                update_view(slug=slug)
                initial_books = Books.objects(slug=slug)
                user = Users.objects(user_id=initial_books[0].user_id)
            else:
                books_content   = False
        if content == 'myaccount':

            if login:
                user_books = Books.objects(user_id=session.get('user_id')).order_by('-date')
                user = Users.objects(user_id=session.get('user_id')).first()
                initial_books = Books.objects(user_id=session.get('user_id')).order_by('-date')

                if term == 'add_new_book':
                    books_content   = False
                    form = AddNewBook()
                elif term  == 'change_password':
                    books_content   = False
                    form = ChangePassword(request.form, old_password='')
                elif term  == 'book_view':
                    if slug:
                        form = DeleteBook()
                        update_view(slug=slug)
                        initial_books = Books.objects(slug=slug)
                        books_content   = is_books_content(initial_books)
                elif term == 'edit_book':
                    if slug:
                        initial_books = Books.objects(slug=slug)
                        books_content   = is_books_content(initial_books)
                        form = EditBook(request.form, category=initial_books[0].category)
                elif term == 'edit_profile':
                    form = EditUser()
                    books_content   = False
                elif term  == 'delete_book':
                    form = DeleteBook()
            else:
                if term == 'login':
                    form = LoginForm()
                    books_content = False
                if term == 'register':
                    books_content = False
                    form = RegisterForm()


        if books_content:
            filter_pagination_books      = get_pagination(initial_books,request.args.get('items'),url_for(content))
            page_pagination = filter_pagination_books[0]
            books  = filter_pagination_books[1]


    return PageData

@app.route('/category', methods=['GET', 'POST'])
@app.route('/category/<category_slug>/', methods=['GET', 'POST'])
def category(category_slug='allcategories'):
    page_data = page_initial_data('category', category_slug, None)
    return render_template('category.html', page_data=page_data)

@app.route('/browse/', methods=['GET', 'POST'])
def browse():

    page_data = page_initial_data('browse',None, None)
    return render_template('browse.html', page_data=page_data)

@app.route('/single_book/', methods=['GET', 'POST'])
@app.route('/single_book/<slug>', methods=['GET', 'POST'])
def single_book(slug=''):
    page_data = page_initial_data('single_book',slug, None)
    if page_data.books_content:
        return render_template('single.html', page_data=page_data)
    else:
        return render_template('404.html', text='This book not found !')



@app.route('/myaccount/', methods=['GET', 'POST'])
@app.route('/myaccount/<term>', methods=['GET', 'POST'])
@app.route('/myaccount/<term>/<slug>', methods=['GET', 'POST'])
def myaccount(term="login",slug=''):
    page_data = page_initial_data('myaccount',slug,term)

    if page_data.login:
        active_user = Users.objects(user_id=session.get('user_id')).first()
        books = Books.objects(user_id=session.get('user_id')).order_by('-date')
        if term == 'profile':
            return render_template('myaccount/profile.html', page_data=page_data)
        elif term == 'edit_profile':
            if page_data.form.validate_on_submit():
                name    = page_data.form.name.data
                email   = page_data.form.email.data
                if page_data.user.email == email:
                    user = Users.objects(user_id=session.get('user_id')).update(name=name, email=email)
                    flash('You are successfully updated your profile!', 'success')
                    return redirect(url_for('myaccount')+'/edit_profile')
                else:
                    user_details = Users.objects(email=email).first()
                    count = Users.objects(email=email).count()
                    if (count>0):
                        flash('This email already existed! Please try another one.', 'danger')
                        return redirect(url_for('myaccount')+'/edit_profile')
                    else:
                        user = Users.objects(user_id=session.get('user_id')).update(name=name, email=email)
                        #user.set_password(password)
                        flash('You are successfully update your profile!', 'success')
                        return redirect(url_for('myaccount')+'/edit_profile')
            else:
                return render_template('myaccount/edit_profile.html', page_data=page_data)
        elif term  == 'mybooks':
            return render_template('myaccount/my_books.html', page_data=page_data)

        elif term  == 'book_view':
                if page_data.books_content:
                    return render_template('myaccount/book_view.html', page_data=page_data)
                else:
                    return render_template('404.html',text='This item not found')



        elif term  == 'add_new_book':

            if page_data.form.validate_on_submit():
                #form upload image file details
                form_file_upload = request.files['upload']
                upload_file_name = str(active_user.user_id) + '_' + str(random.randint(10, 200)) + '_' + secure_filename(form_file_upload.filename)
                form_file_upload.save('application/static/uploads/2020/' + upload_file_name)

                book_name   = page_data.form.book_name.data
                author      = page_data.form.author.data
                user_id     = page_data.user.user_id
                image_url   = upload_file_name
                slug        = page_data.slug_ob.getSlug(page_data.form.book_name.data)
                ISBN        = page_data.form.ISBN.data
                category    = page_data.form.category.data
                overview    = page_data.form.overview.data
                date        = datetime.now()

                book = Books(book_name=book_name, author=author, user_id=user_id, image_url=image_url, slug=slug, ISBN=ISBN, category=category, overview=overview, date=date)
                book.save()
                flash('You are successfully added a new book!', 'success')
                return redirect(url_for('myaccount')+'/mybooks')

            else:
                return render_template('myaccount/add_new_book.html', page_data=page_data)
        elif term  == 'edit_book':

            if slug:
                if page_data.form.validate_on_submit():
                    image_url_link=page_data.books[0].image_url
                    if request.files['upload']:
                        form_file_upload = request.files['upload']
                        image_url_link = str(page_data.user.user_id) + '_' + str(random.randint(10, 200)) + '_' + secure_filename(form_file_upload.filename)
                        #2_198_all-iphone.png
                        if page_data.books[0].image_url:
                            os.remove('application/static/uploads/2020/' + page_data.books[0].image_url)
                        form_file_upload.save('application/static/uploads/2020/' + image_url_link)

                    book_name   = page_data.form.book_name.data
                    author      = page_data.form.author.data
                    user_id     = active_user.user_id
                    image_url   = image_url_link
                    slug        = page_data.books[0].slug
                    ISBN        = page_data.form.ISBN.data
                    category    = page_data.form.category.data
                    overview    = page_data.form.overview.data
                    date        =datetime.now()
                    update_book = page_data.books.update(book_name=book_name, author=author, user_id=user_id, image_url=image_url, slug=slug, ISBN=ISBN, category=category, overview=overview, date=date)
                    flash('You are successfully update your book!', 'success')
                    return redirect(url_for('myaccount')+'/edit_book/'+page_data.books[0].slug)
                else:
                    return render_template('myaccount/edit_book.html', page_data=page_data)
            else:
                redirect(url_for('myaccount')+'mybooks')
        elif term  == 'delete_book':

            if slug:
                book = Books.objects(slug=slug)
                os.remove('application/static/uploads/2020/' + book[0].image_url)
                if page_data.form.validate_on_submit():
                    book.delete()
                    flash('You\'r book successfully deleted!', 'success')
                    return redirect(url_for('myaccount')+'/mybooks')
                else:
                    return redirect(url_for('myaccount')+'/book_view/'+title)
            else:
                return redirect(url_for('myaccount')+'/mybooks')


        elif term  == 'change_password':
            if page_data.form.validate_on_submit():
                new_password = page_data.form.new_password.data
                active_user.set_password(new_password)
                update_book = active_user.update(password=active_user.password)
                flash('You\'r password successfully updated!', 'success')
                return redirect(url_for('myaccount')+'/change_password')
            else:
                return render_template('myaccount/change_password.html', page_data=page_data)
        elif term  == 'logout':
            session['user_id']  = False
            session['login'] = False
            flash('You are successfully logout!', 'danger')
            return redirect(url_for('myaccount')+'/login')
        else:
            return redirect(url_for('myaccount')+'/profile')
    else:
        if term == 'register':

            if page_data.form.validate_on_submit():
                name = page_data.form.name.data
                email = page_data.form.email.data
                password = page_data.form.password.data
                user = Users.objects(email=email).first()
                if (user):
                    flash('You\'r email already existed! Please try another one.', 'danger')
                    return render_template('myaccount/register.html', page_data=page_data)
                else:
                    user_id= Users.objects.all().count()
                    user_id+= 1
                    name       = page_data.form.name.data
                    email    = page_data.form.email.data
                    password  = page_data.form.password.data

                    user = Users(user_id=user_id, name=name, email=email, password=password)
                    user.set_password(password)
                    user.save()

                    session['user_id']  = user_id
                    session['login'] = True
                    flash('You are successfully register!', 'success')
                    return redirect(url_for('myaccount')+'/profile')

            else:
                return render_template('myaccount/register.html', page_data=page_data)


        elif term == 'login':

            if page_data.form.validate_on_submit():
                email = page_data.form.email.data
                password = page_data.form.password.data
                user = Users.objects(email=email).first()
                if user and user.get_password(password):
                    session['user_id']  = user.user_id
                    session['login'] = True

                    flash('You are successfully logged in!', 'success')
                    return redirect(url_for('myaccount')+'/profile')
                else:
                    if user and (user.password!=password):
                        flash('Sorry, Email and password didn\'t match! Please try again', 'danger')
                    else:
                        flash('Sorry, Invalid users details!', 'danger')
                        return redirect(url_for('myaccount')+'/profile')


            return render_template('myaccount/login.html', page_data=page_data)
        else:
            return redirect(url_for('myaccount')+'/login')




if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)
