from flask_wtf import Form
from wtforms import SubmitField

class MoveForm(Form):
	form = Form()
	if form.validate_on_submit():
		if 'Forward' in request.form:
			print('**DEBUG: forward')
			flash('Forward')
		elif 'Backward' in request.form:
			flash('Backward')
		elif 'Left' in request.form:
			flash('Left')
		elif 'Right' in request.form:
			flash('Right')
		elif 'Stop' in request.form:
			flash('Stop')

