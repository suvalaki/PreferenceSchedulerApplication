from time import time
from flask import current_app, url_for
from flask_login import UserMixin

from app import db

# https://stackoverflow.com/questions/25632905/flask-sqlalchemy-relationship
# relationship goes on the ONE SIDE. 
# understanding backref http://docs.sqlalchemy.org/en/latest/orm/backref.html
# backref second argument describes a callback to the join. not the join it self. It is a REFERENCE in the other table to the relationship

class Cal123asdas(db.Model):
    #__tablename__ = 'usasdaer'
    id = db.Column(db.Integer, primary_key=True)

class EnterpriseAgreement(db.Model):

    __tablename__ = "enterpriseagreement"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), unique=True)
    min_periods = db.Column(db.Integer)
    max_periods = db.Column(db.Integer)
    max_periods_overtime = db.Column(db.Integer)
    wage = db.Column(db.Float)
    wage_overtime = db.Column(db.Float)
    employees = db.relationship("Employee", backref = 'agreements', lazy='dynamic') 
    #employees =  db.Column(db.Integer, db.ForeignKey('employee.id'))

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), unique=True)
    skill_assignment = db.relationship("SkillAssignment", backref="skills", lazy='dynamic')
    shedule_requirements = db.relationship("ScheduleRequirement", backref="skills", lazy='dynamic')

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    day = db.Column(db.String(10))
    week = db.Column(db.Integer)
    shift = db.relationship('Shift', backref="periods", lazy='dynamic') 
    shift_periods = db.relationship('ShiftPeriods', backref="periods", lazy='dynamic') 
    schedule_requirements = db.relationship('ScheduleRequirement', backref="periods", lazy='dynamic') 

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_period = db.Column(db.Integer, db.ForeignKey('period.id'))
    shift_length = db.Column(db.Integer)
    shedule_allocation = db.relationship('ScheduleAllocation', backref='shifts', lazy='dynamic')
    preferences = db.relationship('Preference', backref='shifts', lazy='dynamic')

class ShiftPeriods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, db.ForeignKey('period.id'))
    shift = db.Column(db.Integer, db.ForeignKey('shift.id'))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(64))
    agreement = db.Column(db.Integer, db.ForeignKey('enterpriseagreement.id'))
    #agreement = db.relationship('EnterpriseAgreement', backref = 'employee', lazy=True)
    skills = db.relationship('SkillAssignment', backref='employees', lazy='dynamic') 
    preferences = db.relationship('Preference', backref='employees', lazy='dynamic')
    schedule_allocation = db.relationship('ScheduleAllocation', backref='employees', lazy='dynamic')

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    shift = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=False)
    preference_level = db.Column(db.Integer)

class SkillAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    employee = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

class ScheduleRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, db.ForeignKey('period.id'), nullable=False)
    requirement = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)

class ScheduleAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    shift = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=False)
