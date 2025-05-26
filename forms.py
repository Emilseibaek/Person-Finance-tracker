from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from datetime import date
from models import User, Category

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class TransactionForm(FlaskForm):
    amount = DecimalField('Amount', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Amount must be greater than 0')
    ])
    type = SelectField('Type', choices=[
        ('income', 'Income'),
        ('expense', 'Expense')
    ], validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Transaction')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=64, message='Category name must be between 2 and 64 characters')
    ])
    submit = SubmitField('Save Category')

    def __init__(self, user_id, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_name(self, name):
        category = Category.query.filter_by(
            user_id=self.user_id,
            name=name.data
        ).first()
        if category is not None:
            raise ValidationError('You already have a category with this name.') 