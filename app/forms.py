from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import NumberRange, DataRequired, Email, EqualTo


class FormLogin(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class FormRegistration(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class FormForwardCms(FlaskForm):
	forward_distance = IntegerField('Move fwd (cms)',[NumberRange(min=0, max=500)])
	forward_submit = SubmitField('Submit')
		
class FormBackwardCms(FlaskForm):
	pass
	
class FormRotateLeftDegrees(FlaskForm):
	pass
	
class FormRotateRightDegrees(FlaskForm):
	pass
