from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange

class FormForwardCms(FlaskForm):
	forward_distance = IntegerField('Move fwd (cms)',[NumberRange(min=0, max=500)])
	forward_submit = SubmitField('Submit')
		
class BackwardFormCms(FlaskForm):
	pass
	
class RotateLeftDegrees(FlaskForm):
	pass
	
class RotateRightDegrees(FlaskForm):
	pass
