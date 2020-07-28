from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
#from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from application.dbmodels import Allcategory
from wtforms.fields.html5 import DateField, DateTimeLocalField


# Login for user
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6,max=15)])
    submit = SubmitField('Login')

class ChangePassword(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6,max=15)])
    submit = SubmitField('Update Password')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2,max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6,max=40)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6,max=40), EqualTo('password')])
    submit = SubmitField('Register')

class EditUser(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2,max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class DeleteBook(FlaskForm):
    submit = SubmitField('Delete')

class AddNewBook(FlaskForm):
    book_name = StringField('Name', validators=[DataRequired(), Length(min=2,max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2,max=100)])
    ISBN = StringField('ISBN', validators=[DataRequired(), Length(min=2,max=50)])
    category = SelectField('Select Category', choices=Allcategory.getFinalCategory())
    overview = TextAreaField('overview')
    upload = FileField('image', validators=[ FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Add New Book')

class EditBook(FlaskForm):
    book_name = StringField('Name', validators=[DataRequired(), Length(min=2,max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(min=2,max=50)])
    ISBN = StringField('ISBN', validators=[DataRequired(), Length(min=2,max=50)])
    category = SelectField('Select Category', choices=Allcategory.getFinalCategory())
    overview = TextAreaField('overview', validators=[DataRequired()])
    upload = FileField('Change image', validators=[ FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Update')
