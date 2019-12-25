from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, TextAreaField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from vms.models import User, ConcertSeats, ConcertShop


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class GalleryForm(FlaskForm):
    image_link = StringField("Image Link", validators=[DataRequired()])
    submit = SubmitField('Add Image')


class StorePageForm(FlaskForm):
    concert_title = StringField("Product Title", validators=[DataRequired()])
    price = StringField("Price Per 1", validators=[DataRequired()])
    senior_price = StringField("Price for Seniors")
    children_price = StringField("Price for Children")
    description = StringField("Description", validators=[DataRequired()])
    image_link = StringField("Image Link")
    date_of_event = StringField("Date of Event", validators=[DataRequired()])
    time_of_event = StringField("Time of Event", validators=[DataRequired()])
    location = StringField("Location of Event", validators=[DataRequired()])
    submit = SubmitField("Add Store Item")


class ForgotCred(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Send Email To Reset Password")


class CheckoutForm(FlaskForm):
    submit = StringField("")


class ResetPasswordForm(FlaskForm):
    account_email = StringField("Email", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[
                                     DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Submit Password")


class ChangeEmailForm(FlaskForm):
    new_email = StringField("New Email", validators=[DataRequired(), Email()])
    confirm_email = StringField("Confirm Email", validators=[
                                DataRequired(), EqualTo('new_email')])
    submit = SubmitField("Submit Email")
