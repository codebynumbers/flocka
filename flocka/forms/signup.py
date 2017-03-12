from flask_wtf import Form
from wtforms import PasswordField
from wtforms import ValidationError
from wtforms import validators
from wtforms.fields.html5 import EmailField


def host_check(form, field):
    _, host = field.data.split('@')
    if host.lower() not in {'50onred.com', 'red-spark.com'}:
        raise ValidationError('Invalid organization')


class SignupForm(Form):
    username = EmailField(u'Email', validators=[validators.required(), host_check])
    password = PasswordField(
        u'Password', validators=[validators.required(), validators.Length(min=8)])
    password_confirm = PasswordField(
        u'Repeat Password', validators=[validators.required(), validators.EqualTo('password')])

