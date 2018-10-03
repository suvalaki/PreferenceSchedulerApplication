from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
basedir = os.path.abspath(os.path.dirname(__file__))

#http://flask.pocoo.org/docs/1.0/api/

# how http requests work https://www.webnots.com/what-is-http/
# how session cookies work https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
# session gets held by the browser using th http request header <set_cookie> 

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG=True
    SECRET_KEY='123124'
    CSRF_STRING_SIZE = 20 
    CSRF_RANDOM_SEED = 1992


#app.create_app()
#cli.register(app)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
meta = db.metadata
engine = db.engine

login_manager = LoginManager()
login_manager.init_app(app)

from app import models

migrate = Migrate(app, db)

from app import routes
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'meta':meta, 'models': models}

#metadata is in db.Model