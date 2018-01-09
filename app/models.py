from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	documents = db.relationship('Document', backref='author', lazy='dynamic')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
		
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
		
	def __repr__(self):
		return '<User {}><email {}><password_hash {}>'.format(self.username,self.email,self.password_hash)

#class Document
#document in database, models the metadata for a captured document
#also includes the document itself
class Document(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index = True)
	type = db.Column(db.String(64), index = True)
	extension = db.Column(db.String(64), index = True)
	size = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	location = db.Column(db.String(64), index = True)
	body = db.Column(db.LargeBinary)

	def __repr__(self):
		return '<Name {}><Type {}><Size {}>'.format(self.name, self.type, self.size)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
