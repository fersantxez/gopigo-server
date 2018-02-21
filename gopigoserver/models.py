#!venv/bin/python

'''
Flask app models and DB schemas etc.
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin

from gopigoserver.exceptions import ValidationError
from gopigoserver import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), nullable=False, index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    documents = db.relationship('Document', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
        (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    #Token for HTTP Auth (API calls)
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                    expires_in=Config.TOKEN_EXPIRATION) 
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY']) 
        try:
            data = s.loads(token) 
        except:
            return None
        return User.query.get(data['id'])

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
    location = db.Column(db.String(512), index = True)
    body = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return '<Name {}><Type {}><Size {}>'.format(self.name, self.type, self.size)

    def to_json(self): 
        json_document = {
            'name': self.name,
            'type': self.type,
            'extension': self.extension,
            'size': self.size,
            'user_id': self.user_id,
            'location': self.location,
            'body': url_for(self.name,            #offer the body through the internal path
                                _external=True)
        }
        return json_post

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
