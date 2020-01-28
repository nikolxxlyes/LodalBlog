from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, BooleanField,TextAreaField
from wtforms.validators import DataRequired, EqualTo,Email, Length, ValidationError
from blog.models import User,Topic,Post
from flask_login import current_user

class LoginForm( FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign in')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[DataRequired(),Length(min=0,max=140)])
    submit = SubmitField("Submit")

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and user.username != current_user.username:
            raise ValidationError('Please use a different username.')

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is None:
    #         raise ValidationError("This an email address wasn't using.")

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField("Submit")

class NewTopicForm(FlaskForm):
    name = StringField('Topic name', validators=[DataRequired()])
    msg = TextAreaField('Discribe', validators=[DataRequired(),Length(min=0,max=140)])
    submit = SubmitField("Add topic")

    def validate_name(self,name):
        topic = Topic.query.filter_by(name=name.data).first()
        if topic is not None:
            raise ValidationError('Please use a different topic name.')

class EditTopicForm(FlaskForm):
    name = StringField('Topic name', validators=[DataRequired()])
    submit = SubmitField("Edit topic")

    def __init__(self,original_name):
        super(EditTopicForm,self).__init__()
        self.original_name = original_name

    def validate_name(self,name):
        if name.data != self.original_name:
            topic = Topic.query.filter_by(name=name.data).first()
            if topic is not None:
                raise ValidationError('Please use a different topic name.')

class NewPostForm(FlaskForm):
    body = TextAreaField('Enter your thinks', validators=[DataRequired(),Length(min=0,max=140)])
    submit = SubmitField("Add post")

class EditPostForm(FlaskForm):
    body = TextAreaField('Post', validators=[DataRequired(),Length(min=0,max=140)])
    active = BooleanField('Active')
    submit = SubmitField("Apply")
