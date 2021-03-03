from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from flask_login import UserMixin
from app import login
from uuid import uuid4 as unique_id
from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import TEXT

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	paid = db.Column(db.Boolean)
	forgot_password = db.Column(db.Boolean)
	created = db.Column(db.TIMESTAMP)
	insider = db.Column(db.Boolean)
	
	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		print(generate_password_hash)
		return check_password_hash(self.password_hash,password)

class ShareObject(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	description = db.Column(TEXT(charset='latin1')) #Check this Mike
	link = db.Column(db.String(255))
	downloaded = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	reader = db.Column(db.String(45))
	speed = db.Column(db.String(5))

class Email(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
	recipient = db.Column(db.String(255))
	created = db.Column(db.TIMESTAMP, default=db.func.now())
	message_type = db.Column(db.String(45))
	unique_hash = db.Column(db.String(36))
	link_followed = db.Column(db.Integer)

	def __init__(self, user_id, recipient, message_type, link_followed, created):
		self.user_id=user_id
		self.recipient = recipient
		self.message_type=message_type
		self.link_followed = link_followed
		self.created = created
		self.unique_hash = str(unique_id())
		db.session.add(self)
		db.session.commit()

	def validate(self):
		age = datetime.now() - self.created
		if age.days != 0:
			return False
		most_recent = Email.query.filter_by(user_id=self.user_id,message_type=self.message_type).order_by(Email.created.desc()).first()
		if self.id != most_recent.id:
			return False
			
		return True

	def __repr__(self):
		return '<Email {} {} {}>'.format(self.recipient, self.message_type, self.created)
	def set_unique_hash(self):
		#self.unique_hash = generate_password_hash(str(self.user_id) + str(self.created + str(randint(0,255))))
		return self.unique_hash
	
#class Email(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
#	date_sent = db.Column(db.Date)
#	etype = db.Column(db.String(45)) 

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

