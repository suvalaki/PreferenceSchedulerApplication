from flask import render_template, json
from flask.views import View, MethodView
from app import app
from app import db, models
import json

from app import login_manager
from models import *

@login_manager.user_loader
def load_user(id):
    return Employee.get(id)

