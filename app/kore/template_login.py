from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    username = StringField('username',
                           validators=[InputRequired('A username is required!'),
                                       Length(min=7, max=15, message='Invalid Username')],
                           render_kw={"placeholder": "Username"})
    password = PasswordField('password',
                             validators=[InputRequired('Password is required!')],
                             render_kw={"placeholder": "Password"})
    recaptcha = RecaptchaField()
