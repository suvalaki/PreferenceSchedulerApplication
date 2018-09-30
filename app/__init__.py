from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG=True
    SECRET_KEY='123124'


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