from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



#app.create_app()
#cli.register(app)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import models

migrate = Migrate(app, db)

#@app.shell_context_processor
#def make_shell_context():
#    return {}