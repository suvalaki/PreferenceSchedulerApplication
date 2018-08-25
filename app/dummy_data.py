from faker import Faker
from datetime import datetime, date, time, timedelta
from app.models import *
from app import db
from random import randint, uniform


# RUN ME BY IMPORTING AS A MODULE INTO FLASK SHELL
# from app import dummy_data
# dummy_data.__init__()

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

    db.session.execute("DELETE FROM enterpriseagreement")
    for ea in agreements:
        db.session.add(ea)
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

        if curr_id % 168*periods_per_hour == 0: 
            week_id += 1

    db.session.execute("DELETE FROM period")
    for period in periods:
        db.session.add(period)
    db.session.commit()
        
def dummy_employee(n):

    fake = Faker()
    max_EAs = db.session.query(db.func.max(EnterpriseAgreement.id)).first()[0] + 1
    db.session.execute("DELETE FROM employee")

    for i in range(n):

        name = fake.first_name()
        surname = fake.last_name()

        db.session.add(Employee(
            id = i,
            username = name+str(i),
            email = name+'_'+surname+'@fake.com',
            password_hash = 'asda',
            agreement = randint(1,max_EAs)
        ))
    
    db.session.commit()

def dummy_skill():

    skill_names = ['cashier','cook','cleaner','master cook','advanced cook','manager']
    skills = []

    for i in range(len(skill_names)):

        skills.append(Skill(
            id = i,
            name = skill_names[i],
        ))

    db.session.execute("DELETE FROM skill")
    for skill in skills:
        db.session.add(skill)
    db.session.commit()

def dummy_skill_assignment(ratio=1.5):

    skill_num = db.session.execute("SELECT MAX(skill.id) FROM skill").first()[0] + 1
    employee_num = db.session.execute("SELECT MAX(employee.id) FROM employee").first()[0] + 1
    skill_ratio = []
    skill_assignment = []

    assignment_id = 0

    for s in range(skill_num):
        skill_ratio.append(1/(ratio**s))

    for emp in range(employee_num):
        for s in range(skill_num):
            if uniform(0,1) < skill_ratio[s]:
                skill_assignment.append(SkillAssignment(
                    id = assignment_id,
                    skill = s,
                    employee = emp
                ))
                assignment_id += 1

    db.session.execute("DELETE FROM skill_assignment")
    for sa in skill_assignment:
        db.session.add(sa)
    db.session.commit()

def dummy_shifts(start_datetime, end_datetime, periods_per_hour, shift_length):

    # evenly spaced shifts
    period_length = timedelta(hours = 1/periods_per_hour)
    curr_id = 1
    week_id = 1
    curr_datetime = start_datetime
    start_date = start_datetime.date()

    shifts = []
    shift_periods = []

    while curr_datetime < end_datetime:

        if curr_id % shift_length == 0 or curr_id == 1:

            shift_id = len(shifts)+1

            shifts.append(Shift(
                id=shift_id,
                start_period = curr_id,
                shift_length = shift_length
            ))

            for p in range(shift_length):
                shift_periods.append(ShiftPeriods(
                    id = len(shift_periods)+1,
                    period = curr_id+p,
                    shift = shift_id
                ))

        curr_id +=1
        curr_datetime += period_length

        if curr_id % 168*periods_per_hour == 0: 
            week_id += 1

    db.session.execute("DELETE FROM shift")
    db.session.execute("DELETE FROM shift_periods")
    for shift in shifts:
        db.session.add(shift)
    for sp in shift_periods:
        db.session.add(sp)

    db.session.commit()

def dummy_preference(max_preference):
    employee_num = db.session.execute("SELECT MAX(employee.id) FROM employee").first()[0] + 1
    shift_num = db.session.execute("SELECT MAX(shift.id) FROM shift").first()[0] + 1

    preferences = []
    curr_id = 0

    for i in range(employee_num):
        for j in range(shift_num):
            preferences.append(Preference(
                id = curr_id,
                employee = i,
                shift = j,
                preference_level = randint(0,max_preference)
            ))
            curr_id += 1
    
    db.session.execute("DELETE FROM preference")
    for p in preferences:
        db.session.add(p)
    db.session.commit()

def dummy_schedule_requirement(requirement=4):
    max_period = db.session.execute("SELECT MAX(period.id) FROM period").first()[0] + 1
    max_skill = db.session.execute("SELECT MAX(skill.id) FROM skill").first()[0] + 1

    requirements = []
    curr_id = 0

    for i in range(max_period):
        for j in range(max_skill):
            for z in range(randint(1,requirement)):
                requirements.append(ScheduleRequirement(
                    id = curr_id,
                    period = i,
                    requirement = j
                ))
                curr_id += 1

    db.session.execute("DELETE FROM schedule_requirement")
    for r in requirements:
        db.session.add(r)
    db.session.commit()

def __init__(employee_number=20,
                start_datetime = datetime(2018,1,1),
                end_datetime = datetime(2018,1,7),
                periods_per_hour = 1,
                shift_length = 6,
                ratio = 1.05,
                max_preference = 10,
                requirement=1):

    dummy_enterprise_agreements()
    dummy_skill()
    dummy_periods(start_datetime, end_datetime, periods_per_hour)
    dummy_employee(employee_number)
    dummy_shifts(start_datetime, end_datetime, periods_per_hour, shift_length)
    dummy_skill_assignment(ratio)
    dummy_preference(max_preference)
    dummy_schedule_requirement(requirement)

if __name__ == "__main__": 
    __init__()