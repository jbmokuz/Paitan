from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')

class TenhouNameForm(FlaskForm):
    tenhouName = StringField('Tenhou User Name')
    submit = SubmitField('Update User Name')

class TenhouForm(FlaskForm):

    def validate_admin_page(form, field):
        if "?" in field.data:
            end = field.data.split("?")[-1]
            if re.match("C\d{16}",end):
                return
        raise ValidationError('Not a valid admin page')

    def validate_rules(form, field):
        if not re.match("[0-9A-F]{4}",field.data):
            raise ValidationError('Not a valid rule')
    
    admin_page = StringField('Admin Page', validators=[DataRequired(),validate_admin_page])
    rules = StringField(
        'Rules', validators=[DataRequired(),validate_rules])
    submit = SubmitField('Update')


class RateForm(FlaskForm):
    myField = SelectField(u'Select Default Rate', choices = ["Standard","Tensan","Tengo","TenPin"])
    submit = SubmitField('Update')
            
