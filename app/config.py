import os

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	static_url_path='/'
	static_folder='static/'
	root_url = 'http://127.0.0.1:8000/'
	UPLOAD_FOLDER = 'data/uploads/'
	root_dir = os.getcwd() + '/'
	insider_share_dir = 'data/shared/'
	SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector:<db login credentials>"
	MS_TRANSLATOR_KEY='<ms translator key>'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER='<mail server>'
	MAIL_PORT=587
	MAIL_USE_TLS=1
	MAIL_USERNAME="<username>@<website>.com"
	MAIL_PASSWORD=""
	#MAIL_PASSWORD="C#hatt2e"
