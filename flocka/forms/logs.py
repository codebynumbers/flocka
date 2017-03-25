from flask_wtf import Form
from wtforms import IntegerField, BooleanField


class LogForm(Form):
    lines = IntegerField('lines', default=200)
    reverse = BooleanField('reverse', default=False)