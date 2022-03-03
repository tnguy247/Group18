from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import User
from database import db
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, Form
from flask_wtf.file import FileField, FileAllowed
from flask import session



class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = StringField('First Name', validators=[Length(1, 10)])

    lastname = StringField('Last Name', validators=[Length(1, 20)])

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password."),
        EqualTo('confirmPassword', message='Passwords must match')
    ])

    confirmPassword = PasswordField('Confirm Password', validators=[
        Length(min=6, max=10)
    ])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() != 0:
            raise ValidationError('Username already in use.')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField('Email', [
        Email(message='Not a valid email address.'),
        DataRequired()])

    password = PasswordField('Password', [
        DataRequired(message="Please enter a password.")])

    submit = SubmitField('Submit')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() == 0:
            raise ValidationError('Incorrect username or password.')

class CommentForm(FlaskForm):
    class Meta:
        csrf = False

    comment = TextAreaField('Reply',validators=[Length(min=1)])

    submit = SubmitField('Add Reply')


class SearchForm(Form):
    choices = [('Question', 'Question'),
               ('User', 'User')],
    select = SelectField('Search for topic: ', choices= choices)
    search = StringField('')

class UpdateAccountForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField('Email', [Email(message='Not a valid email address.'), DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    new_password = PasswordField('Password', [DataRequired(message="Please enter a password."),
                                          EqualTo('confirm_newPassword', message='Passwords must match')])
    confirm_newPassword = PasswordField('Confirm Password', validators=[Length(min=6, max=10)])
    submit = SubmitField('Submit')


    def validate_email(self, field):
        if db.session.query(User).filter_by(email=field.data).count() != 0:
            raise ValidationError('Username already in use.')

    def validate_newPassword(self, field):
        if db.session.query(User).filter_by(password=field.data).one() == 1:
            raise ValidationError('Cannot reuse password. Please choose a different one.')
