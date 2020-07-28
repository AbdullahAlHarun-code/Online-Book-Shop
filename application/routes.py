from application import app, db
from flask import render_template, request, Markup, json, jsonify, Response, redirect, flash, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime, date
import bson
import os.path
import random
from application.forms import ChangePassword, LoginForm, RegisterForm, EditUser, AddNewBook, EditBook, DeleteBook
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from application.models import Users, Books, Testuser, Categories
from application.dbmodels import Title, Helper
#from flask_uploads import configure_uploads, IMAGES, UploadSet

app.config['MONGO_DBNAME']='book_shop'
app.config['MONGO_URI'] = 'mongodb+srv://root:Zee9Zee9@firstcluster.qhtcj.mongodb.net/book_shop?retryWrites=true&w=majority'

app.secret_key = 'asdfaiueh345345wk3jfnsdjkfkdjfvkdfjgsdfg45345'



mongo = PyMongo(app)

def check_login():
    if session.get('login'):
        return True
    else:
        return False

@app.route('/page_not_found')
def page_not_found():
    login=check_login()
    return render_template('404.html', login=login)




@app.route('/')
def home():
    login=check_login()
    books=Books.objects().order_by('-date')
    title = Title
    categories=Categories.objects.all()
    return render_template('index.html', title=title, login=login, books=books, categories=categories)
    #return render_template('index.html', login=login, categories=mongo.db.categories.find(), categories1=mongo.db.categories.find())

#this function for page content pagination
def pagination(count):
    if count>6:
        pagination_block=Markup('<ul class="pagination">')
        for value in range(0,count%6):
            active=''
            if value==0:
                active='active'

            pagination_block+=Markup('<li><a href="#" class="'+active+'">'+str(value+1)+'</a></li>')

        pagination_block+=Markup('</ul>')
        return pagination_block
    else:
        return ''
@app.route('/category', methods=['GET', 'POST'])
@app.route('/category/<cat>', methods=['GET', 'POST'])
def category(cat='allcategories'):
    login=check_login()
    categories = Categories.objects.all()
    category_name =Title.getTitle(cat)
    books=Books.objects(category=category_name)
    recenty_added=Books.objects().order_by('-date')
    title = Title
    if cat=='allcategories':
        cat='All Categories'
        return render_template('category.html', recenty_added=recenty_added, title=title, cat=cat, login=login, categories=categories, books=books)
    elif cat=='recently_added':
        cat='Recently Added'
        books = recenty_added
        page_pagination = pagination(books.count())
        return render_template('category.html', recenty_added=recenty_added, page_pagination=page_pagination, title=title, cat=cat, login=login, categories=categories, books=books)
    else:
        cat=cat+' Books'
        books=books.order_by('-date')
        page_pagination = pagination(books.count())
        return render_template('category.html', recenty_added=recenty_added, page_pagination=page_pagination, title=title, cat=cat, login=login, categories=categories, books=books)


@app.route('/single_book/', methods=['GET', 'POST'])
@app.route('/single_book/<title>', methods=['GET', 'POST'])
def single_book(title=''):
    login=check_login()
    recenty_added=Books.objects().order_by('-date')
    if title:

        book_title =Title.getTitle(title)
        book = Books.objects(book_name=book_title,ISBN=request.args.get('isbn'))
        categories = Categories.objects.all()
        user=Users.objects(user_id=book[0].user_id)
        helper=Helper
        title = Title
        return render_template('single.html', recenty_added=recenty_added, user=user, categories=categories, login=login, helper=helper, title=title, book=book, book_title=book_title)
    else:
        return render_template('single.html', recenty_added=recenty_added, login=login, categories=mongo.db.categories.find(), categories1=mongo.db.categories.find(), single_book=True)



def add_user():
    users =  mongo.db.users
    users.insert_one(request.form.to_dict())
    return redirect(url_for('profile'))

@app.route('/testdata')
def testdata():
    ##users =  mongo.db.users
    ##users.insert_one(request.form.to_dict())
    return render_template('testdata.html')

@app.route('/myaccount/', methods=['GET', 'POST'])
@app.route('/myaccount/<term>', methods=['GET', 'POST'])
@app.route('/myaccount/<term>/<title>', methods=['GET', 'POST'])
def myaccount(term="login",title=''):
    login=check_login()
    form = LoginForm()
    if login:
        active_user = Users.objects(user_id=session.get('user_id')).first()
        books = Books.objects(user_id=session.get('user_id'))
        if term == 'profile':
            return render_template('myaccount/profile.html', login=login, user=active_user, books=books)
        elif term == 'edit_profile':
            form = EditUser()
            if form.validate_on_submit():
                name = form.name.data
                email = form.email.data
                if active_user.email==email:
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
                return render_template('myaccount/edit_profile.html', form=form, login=login, user=active_user, books=books)
        elif term  == 'mybooks':
            if books:
                slug = Title.getUrlTitle(books[0].book_name)
                title = Title
            else:
                slug = ''

            return render_template('myaccount/my_books.html', title=title, slug=slug, login=login, user=active_user,  books=books)
        elif term  == 'book_view':
            if title:
                book_title =Title.getTitle(title)
                book = Books.objects(book_name=book_title)
                form = DeleteBook()
                helper=Helper
                return render_template('myaccount/book_view.html', form=form, login=login, helper=helper, title=title, user=active_user, book=book, book_title=book_title)
            else:
                return render_template('myaccount/book_view.html', login=login, user=active_user, books=books, book_title=book_title)

        elif term  == 'add_new_book':
            form = AddNewBook()
            if form.validate_on_submit():
                books = Books.objects(user_id=session.get('user_id'),book_name=form.book_name.data)
                if not books:
                    f = request.files['upload']
                    full_name = str(active_user.user_id) + '_' + str(random.randint(10, 200)) + '_' + secure_filename(f.filename)
                    f.save('application/static/uploads/2020/' + full_name)

                    book_name   = form.book_name.data
                    author      = form.author.data
                    user_id     = active_user.user_id
                    image_url     = full_name
                    ISBN        = form.ISBN.data
                    category    = form.category.data
                    overview    = form.overview.data
                    date        = datetime.now()

                    book = Books(book_name=book_name, author=author, user_id=user_id, image_url=image_url, ISBN=ISBN, category=category, overview=overview, date=date)
                    book.save()
                    flash('You are successfully added a new book!', 'success')
                    return redirect(url_for('myaccount')+'/mybooks')
                else:
                    flash('This book already exists in your account! Try another one', 'danger')
                    return render_template('myaccount/add_new_book.html', login=login, form=form, user=active_user)
            else:
                return render_template('myaccount/add_new_book.html', login=login, form=form, user=active_user)
        elif term  == 'edit_book':

            if title:
                book_title =Title.getTitle(title)
                book = Books.objects(book_name=book_title)
                #FormHelper('Parenting')
                form = EditBook(request.form, category=book[0].category)
                #form.category.default='Parenting'
                helper=Helper
                if form.validate_on_submit():
                    image_url_link=book[0].image_url
                    if request.files['upload']:
                        f = request.files['upload']
                        image_url_link = str(active_user.user_id) + '_' + str(random.randint(10, 200)) + '_' + secure_filename(f.filename)
                        #2_198_all-iphone.png
                        if book[0].image_url:
                            os.remove('application/static/uploads/2020/' + book[0].image_url)
                        f.save('application/static/uploads/2020/' + image_url_link)

                    book_name = form.book_name.data
                    author = form.author.data
                    user_id = active_user.user_id
                    image_url = image_url_link
                    ISBN = form.ISBN.data
                    category = form.category.data
                    overview = form.overview.data
                    date=datetime.now()
                    update_book = book.update(book_name=book_name, author=author, user_id=user_id, image_url=image_url, ISBN=ISBN, category=category, overview=overview, date=date)
                    flash('You are successfully update your book!', 'success')
                    return redirect(url_for('myaccount')+'/edit_book/'+title+'#isbn='+book.ISBN)
                else:
                    return render_template('myaccount/edit_book.html', login=login, title=title, book_title=book_title, book=book, helper=helper, form=form, user=active_user)
            else:
                redirect(url_for('myaccount')+'mybooks')
        elif term  == 'delete_book':

            if title:
                form = DeleteBook()
                book_title =Title.getTitle(title)
                book = Books.objects(book_name=book_title,user_id=active_user.user_id)
                os.remove('application/static/uploads/2020/' + book[0].image_url)
                if form.validate_on_submit():
                    book.delete()
                    flash('You\'r book successfully deleted!', 'success')
                    return redirect(url_for('myaccount')+'/mybooks')
                else:
                    return redirect(url_for('myaccount')+'/book_view/'+title)
            else:
                return redirect(url_for('myaccount')+'/mybooks')


        elif term  == 'change_password':
            form = ChangePassword(request.form, old_password='asdf')
            if form.validate_on_submit():
                new_password = form.new_password.data
                active_user.set_password(new_password)
                update_book = active_user.update(password=active_user.password)
                flash('You\'r password successfully updated!', 'success')
                return redirect(url_for('myaccount')+'/change_password')
            else:
                return render_template('myaccount/change_password.html', login=login, form=form, user=active_user)
        elif term  == 'logout':
            session['user_id']  = False
            session['login'] = False
            flash('You are successfully logout!', 'danger')
            return redirect(url_for('myaccount')+'/login')
        else:
            return redirect(url_for('myaccount')+'/profile')
    else:
        if term == 'register':

            form = RegisterForm()
            if form.validate_on_submit():
                name = form.name.data
                email = form.email.data
                password = form.password.data
                user = Users.objects(email=email).first()
                if (user):
                    flash('You\'r email already existed! Please try another one.', 'danger')
                    return render_template('myaccount/register.html', form=form, login=login)
                else:
                    user_id= Users.objects.all().count()
                    user_id+= 1
                    name       = form.name.data
                    email    = form.email.data
                    password  = form.password.data

                    user = Users(user_id=user_id, name=name, email=email, password=password)
                    user.set_password(password)
                    user.save()

                    session['user_id']  = user_id
                    session['login'] = True
                    flash('You are successfully register!', 'success')
                    return redirect(url_for('myaccount')+'/profile')

            else:
                return render_template('myaccount/register.html', form=form, login=login)


        elif term == 'login':
            if form.validate_on_submit():
                email = form.email.data
                password = form.password.data
                user = Users.objects(email=email).first()
                if user and user.get_password(password):
                    session['user_id']  = user.user_id
                    session['login'] = True

                    flash('You are successfully logged in!', 'success')
                    return redirect(url_for('myaccount')+'myaccount/profile')
                else:
                    if user and (user.password!=password):
                        flash('Sorry, Email and password didn\'t match! Please try again', 'danger')
                    else:
                        flash('Sorry, Invalid users details!', 'danger')
                        return redirect(url_for('myaccount')+'/profile')


            return render_template('myaccount/login.html', form=form, login=login)
        else:
            return redirect(url_for('myaccount')+'/login')




class User():
    users = mongo.db.users

    def add(data):
        users = mongo.db.users
        users.insert_one(data)
    def getUsers():
        users = mongo.db.users
        return users.find()


@app.route("/user")
def user():
    user1={'_id':3,'name':'Abdullah', 'email':'aharun46@gmail.com', 'password':"123456"}
    user2={'_id':4,'name':'Mofif', 'email':'saharun46@gmail.com', 'password':"ergsdf456"}
    #User(_id=2,name='Abdullah', email='saharun46@gmail.com', password="123456").save()
    Testuser(user_id=9,name='Topu', email='topu02@gmail.com',password='dfgh34534df').save()
    testusers = Testuser.objects.all()

    #users = Users.objects.all()
    #User.add(user1)
    #User.add(user2)
    #return render_template('testdata.html', users=User.getUsers())
    return render_template('testdata.html', users=testusers)
