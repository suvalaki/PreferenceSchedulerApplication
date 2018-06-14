from faker import Faker
from datetime import datetime, date, time, timedelta
from app.models import *
from app import db
from random import randint

#models.EnterpriseAgreement.query.all()

def dummy_enterprise_agreements():

    agreements = []
    
    agreements.append(EnterpriseAgreement(
        id = 1,
        name = 'casual',
        min_periods = 0,
        max_periods = 76,
        wage = 15,
        wage_overtime = 20,
    ))

    agreements.append(EnterpriseAgreement(
        id = 2,
        name = 'full time',
        min_periods = 46,
        max_periods = 196,
        wage = 17.5,
        wage_overtime = 22,
    ))

    agreements.append(EnterpriseAgreement(
        id = 3,
        name = 'domestic',
        min_periods = 0,
        max_periods = 76,
        wage = 20,
        wage_overtime = 26,
    ))

    for ea in agreements:
        db.session.add(ea)
    db.session.commit()

def dummy_skill():

    skills = []

    skills.append(Skill(
        id = 1,
        name = 'cashier',
    ))

    skills.append(Skill(
        id = 2,
        name = 'cook',
    ))

    skills.append(Skill(
        id = 3,
        name = 'cleaner',
    ))

    skills.append(Skill(
        id = 4,
        name = 'advanced cook',
    ))

    skills.append(Skill(
        id = 5,
        name = 'manager',
    ))

    for skill in skills:
        db.session.add(skill)
    db.session.commit()

def dummy_periods(start_datetime, end_datetime, periods_per_hour):

    period_length = timedelta(hours = 1/periods_per_hour)
    curr_id = 1
    week_id = 1
    curr_datetime = start_datetime
    start_date = start_datetime.date()

    periods = []

    while curr_datetime < end_datetime:

        periods.append(Period(
            id = curr_id,
            start_time = curr_datetime.time(),
            end_time = (curr_datetime + period_length).time(),
            day = curr_datetime.weekday(),
            week = week_id
        ))

        curr_id +=1
        curr_datetime += period_length

        if curr_id % 168 == 0: 
            week_id += 1

    for period in periods:
        db.session.add(period)
    db.session.commit()
        
def dummy_employee(n):

    fake = Faker()
    max_EAs = db.session.query(db.func.max(EnterpriseAgreement.id)).first()[0]

    for i in range(n):

        name = fake.first_name()
        surname = fake.last_name()

        db.session.add(Employee(
            id = i,
            username = name,
            email = name+'_'+surname+'@fake.com',
            password_hash = 'asda',
            agreement = randint(1,max_EAs)
        ))
    
    db.session.commit()


