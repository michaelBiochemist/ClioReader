from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from werkzeug.datastructures import ImmutableMultiDict
import logging
from flask_mail import Mail
#from flask_sslify import SSLify

#app = Flask(__name__, static_url_path='/', static_folder='static/')
app = Flask(__name__)
#sslify = SSLify(app)
app.config.from_object(Config)

mail = Mail(app)
db = SQLAlchemy(app)
db.create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_recycle=3600)
#from app.models import User
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view='index'

logging.basicConfig(level=logging.DEBUG)
from app import routes
from app.models import User
#from app.translations import Translation, AudioBook, AudioChapter
from app import translations
from app import purchasing
from app import translations

#from app import routes

"""
def get_engine():
    engine = create_engine('mysql+mysqlconnector://...my_conn_string...', echo=True)
    return engine

def generic_execute(sql):
    db = get_engine()
    connection = db.connect()
    connection.execute(sql)
"""
