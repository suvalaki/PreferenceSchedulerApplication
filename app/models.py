from time import time
from flask import current_app, url_for
from flask_login import UserMixin

from app import db, login

class Calendar(db.Model):
    #__tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

class EnterpriseAgreement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), unique=True)
    min_periods = db.Column(db.Integer)
    max_periods = db.Column(db.Integer)
    max_periods_overtime = db.Column(db.Integer)
    wage = db.Column(db.Float)
    wage_overtime = db.Colum(db.Float)
    employee = db.relationship("Employee", backref = 'enterpriseagreement', lazy='dynamic') 

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), unique=True)
    skill_assignment = db.relationship("SkillAssignment", backref="skill", lazy='dynamic')
    shedule_requirements = db.relationship("ScheduleRequirement", backref="skill", lazy='dynamic')

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    day = db.Column(db.String(10))
    week = db.Column(db.Integer)
    shifts = db.relationship('Shift', backref="period", lazy='dynamic') 

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shedule_allocation = db.relationship('Shift', backref='shift', lazy='dynamic')
    preferences = db.relationship('Preference', backref='shift', lazy='dynamic')

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(64))
    agreement = db.Column(db.string(8), foreign_key = 'enterpriseagreement.name', nullable=False)
    skills = db.relationship('SkillAssignment', backref='employee', lazy='dynamic') 
    preferences = db.relationship('Preferences', backref='employee', lazy='dynamic')
    schedule_allocation = db.relationship('ScheduleAllocation', backref='employee', lazy='dynamic')

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shift = db.relationship('Shift', backref='preference', lazy='dynamic') #
    employee = db.replationship('Employee', backref='preference', lazy='dynamic') #

class SkillAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.string(8), foreign_key = 'skill.name', nullable=False)
    Employee = db.Column(db.string(8), foreign_key = 'employee.name', nullable=False)

class ScheduleRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, foreign_key = 'Period.id', nullable=False)
    requirement = db.Column(db.string(8), foreign_key = 'skill.name', nullable=False)

class ScheduleAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee = db.Column(db.string(8), foreign_key = 'employee.username', nullable=False)
    shift = db.Column(db.string(8), foreign_key = 'shift.id', nullable=False)

