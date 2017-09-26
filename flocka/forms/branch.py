from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class BranchSlugField(StringField):

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0]:
                self.data = valuelist[0].strip()
            else:
                self.data = valuelist[0]


class BranchForm(Form):
    name = BranchSlugField(u'Name', validators=[DataRequired()])
    aliases = StringField(u'Hostname aliases', validators=[Length(max=100)],
                          description="Space seperated hostname aliases used in nginx config")
    config = TextAreaField(u'Custom config',
                           description="Key value otions to override defaults")