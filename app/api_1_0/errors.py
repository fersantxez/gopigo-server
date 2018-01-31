from flask import response
import jsonify

#Error handlers - these overwrite the "main" ones?
#404 and 500 remain in main, here are the remaining ones

@app.errorhandler(403) 
def forbidden(message):
	response = jsonify({'error': 'forbidden', 'message': message}) 
	response.status_code = 403
	return response
