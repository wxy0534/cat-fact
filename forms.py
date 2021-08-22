from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):        
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FactForm(FlaskForm):    
    text = StringField("Cat Text", validators=[InputRequired()])
   

   