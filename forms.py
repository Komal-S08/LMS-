from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired()])
    code = StringField('Course Code', validators=[DataRequired()])
    description = TextAreaField('Description')

    material_file = FileField(
        "Upload Study PDF",
        validators=[FileAllowed(['pdf'], 'PDF files only!')]
    )

    video_url = StringField("YouTube Video URL")
    price = FloatField("Course Price (0 for free)")

    submit = SubmitField('Create Course')