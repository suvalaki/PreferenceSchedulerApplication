# http://flask.pocoo.org/docs/1.0/views/
# https://ourcodeworld.com/articles/read/434/top-5-best-free-jquery-and-javascript-dynamic-gantt-charts-for-web-applications

#https://github.com/wbkd/awesome-d3

from flask import render_template, request, json, session, abort
from flask.views import View, MethodView
from app import app
#app and session are defined in __init__.py . everything in init.py gets defined when referencing the containing folder in python
from app import db, models
import random
import string
import matplotlib
import matplotlib.cm as cm
from flask.json import jsonify

import collections
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import validators as valid
from werkzeug.datastructures import MultiDict
from flask_inputs import Inputs # https://pythonhosted.org/Flask-Inputs/


def nested_class_test(json_dict, value_rule_dict):
    """
    Function to produce a dynamic class for validation checking
    Flattens a nested dict down

    Example usage:
        test_case_false = nested_class_test({'username':None},
                                {'username': [DataRequired(),]})
        test_case_false.validate()       

        returns False                   
    """
    def flatten(d, parent_key='', sep='___'):
        # https://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    class inner_value_class:
        def __init__(self, json_dict):
            self.values = MultiDict(mapping = flatten(json_dict))

    class inner_rule_class(Inputs):
        values = flatten(value_rule_dict)

    return inner_rule_class(inner_value_class(json_dict))




# https://stackoverflow.com/questions/32062097/using-flask-wtforms-validators-without-using-a-form

# hashed passwords


#from flask.ext.api import status
# return content, status.HTTP_404_NOT_FOUND - https://www.flaskapi.org/api-guide/status-codes/


# CSRF TOKENS - http://flask.pocoo.org/snippets/3/

random.seed(app.config['CSRF_RANDOM_SEED'])

random_string = lambda length: ''.join(random.sample(string.printable, length))

# https://stackoverflow.com/questions/19574694/flask-hit-decorator-before-before-request-signal-fires

def exclude_from_csrf(func):
    func._exclude_from_csrf = True
    return func

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        print(token)
        print(request.get_json().keys())
        if not token or token != request.get_json()['_csrf_token']:
            print(request.get_json())
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_string(app.config['CSRF_STRING_SIZE'])
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token   



def new_employee_default_password(username):
    return username + '1234'

# REQUESTS https://stackoverflow.com/questions/10434599/how-to-get-data-received-in-flask-request

def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)


class LoginView(View):

    methods = ['GET']
    #decorators = [superuser_required]

    def dispatch_request(self):
        return render_template('login.html')

class PrimaryView(View):

    methods = ['GET']
    #decorators = [superuser_required]

    def dispatch_request(self):
        return render_template('index.html' )

class PeriodChart(View):

    methods = ['GET']
    #decorators = [superuser_required]

    def dispatch_request(self):

        # https://stackoverflow.com/questions/37133774/how-can-i-select-only-one-column-using-sqlalchemy
        #https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify

        # periods = db.session.query(models.Period)\
        #            .distinct(models.Period.id)\
        #            .options(load_only("id"))\
        #            .scalar()

        periods = [x[0] for x in db.session.execute("SELECT DISTINCT(period.id) FROM period")]
        
        # skills = db.session.query(models.Skill)\
        #            .distinct(models.Skill.id)\
        #            .options(load_only("id"))\
        #            .scalar()

        skills = [x[0] for x in db.session.execute("SELECT DISTINCT(skill.id) FROM skill")]

        datasets = []

        #colormap 
        # https://stackoverflow.com/questions/28752727/map-values-to-colors-in-matplotlib

        min_c = min(skills)
        max_c = max(skills)

        norm_c = matplotlib.colors.Normalize(vmin=min_c,vmax=max_c, clip=True)
        mapper_c = cm.ScalarMappable(norm_c,cmap=cm.Blues_r)

        # itterateively build a dictionairy to be passed to json
        for s in skills:

            label = db.session.query(models.Skill.name).filter_by(id = int(s)).first()[0]
            backgroundColor = "rgba"+str(tuple([x[0] * x[1] for x in zip(mapper_c.to_rgba(s), [255,255,255,1])]))
            series = [x[0] for x in db.session.query(
                db.func.count(models.ScheduleRequirement.requirement))\
                        .filter_by(requirement = int(s))\
                        .group_by(models.ScheduleRequirement.period)\
                        .order_by(models.ScheduleRequirement.period)\
                        .all()]

            datasets.append({
                'label': label,
                'backgroundColor': backgroundColor,
                'data': series
            })

        data = {
            'labels': [x[0] for x in db.session.query(models.Period.id)\
                            .distinct(models.Period.id)\
                            .order_by(models.Period.id)\
                            .all()],
            'datasets':datasets
        }



        return render_template('period_chart.html', dataset = data  )


class AJAX_ShiftTable(View):

    methods = ['GET']
    #decorators = [superuser_required]

    @staticmethod
    def load_shifts_to_json():

        #Get Shifts
        shifts = [list(x) for x in db.session.execute(
            """
            SELECT  id, 
                    start_period, 
                    start_period + shift_length as end_period,
                    shift_length
            FROM shift
            ORDER BY id
            """
        )]


        return json.jsonify(data = shifts)
        

    def dispatch_request(self):

        return self.load_shifts_to_json()


# https://scotch.io/tutorials/how-to-use-the-javascript-fetch-api-to-get-data

class AJAX_ShiftEdit(MethodView):

    #decorators = [superuser_required]

    # https://stackoverflow.com/questions/31987590/delete-row-using-datatable-plugin-then-delete-it-from-database 

    @staticmethod
    def delete_shift(id):

        
        #Get Shifts
        try:
            db.Shfit.delete().where(db.Shfit.c.id == id)
            return True

        except:
            return False
        

    def post(self):
        
        data = request.get_json()
        print(data)

        if data['method'] == 'delete':
            #https://kite.com/python/docs/sqlalchemy.orm.query.Query.delete
            # https://stackoverflow.com/questions/39773560/sqlalchemy-how-do-you-delete-multiple-rows-without-querying
            #sql alchemy bulk deletion
            # https://docs.sqlalchemy.org/en/latest/orm/query.html


            try:
                db.session.query(models.Shift)\
                .filter(models.Shift.id.in_(data['ids']))\
                .delete(synchronize_session=False)

                db.session.query(models.ShiftPeriods)\
                .filter(models.ShiftPeriods.shift.in_(data['ids']))\
                .delete(synchronize_session=False)

                #when syncronise session=False requires session commit
                db.session.commit()

                return jsonify({'delete_status':True}) 

            except:
                db.session.rollback()
                return jsonify({'delete_status':False})



        if data['method'] == 'edit':
            try:
                # Modify a single database entry

                #update the shift table element
                shift_update_candidate = db.session.query(models.Shift)\
                .filter(models.Shift.id == data['id']).first()

                shift_update_candidate.start_period = int(data['start_period'])
                shift_update_candidate.shift_length = int(data['shift_length'])

                #update the shift periods within the shift period table
                db.session.query(models.ShiftPeriods)\
                    .filter(models.ShiftPeriods.shift == data['id'])\
                    .delete(synchronize_session=False)

                max_id = db.session.query(
                    db.func.max(models.ShiftPeriods.id)
                ).first()[0]

                for period in range(int(data['shift_length'])):
                    db.session.add(models.ShiftPeriods(
                        id = int(max_id) + int(period) + 1,
                        period = int(data['start_period']) + period,
                        shift = int(data['id'])
                    ))

                db.session.commit()
            
                return jsonify({'edit_status':True}) 

            except:
                db.session.rollback()
                return jsonify({'edit_status':False})
            #update the 



        #data = request.data
        #dataDict = json.loads(data)

        #print(dataDict)
        #print(request.values)


        

        if data['method'] == 'add':

            #try:
            #add a new shift to the database
            #get the last unique shift id
            max_shift_id = db.session.query(
                        db.func.max(models.Shift.id)
                    ).first()[0]

            if max_shift_id == None:
                #if the shift db is empty init the shift id
                max_shift_id = 0
            else:
                max_shift_id += 1

            db.session.add(models.Shift(
                id = max_shift_id,
                start_period = int(data['start_period']),
                shift_length = int(data['shift_length']),
            ))

            end_period = int(data['start_period']) +\
                            int(data['shift_length'])

            # add the shift periods in
            max_period_id = db.session.query(
                        db.func.max(models.ShiftPeriods.id)
                        ).first()[0]

            for period in range(int(data['shift_length'])):
                db.session.add(models.ShiftPeriods(
                    id = int(max_period_id) + int(period) + 1,
                    period = int(data['start_period']) + period,
                    shift = max_shift_id
                ))

            db.session.commit()

            return jsonify({
                'add_status':True,
                'id': max_shift_id, 
                'start_period': int(data['start_period']),
                'end_period':end_period,
                'shift_length': int(data['shift_length'])
                }) 

            #except:
            #    return jsonify({'add_status':False}) 

        return jsonify({'test' : 1, 'data' : 'dataset'})


class ShiftTable(View):

    methods = ['GET']

    def dispatch_request(self):
        return render_template('admin_shift.html')



class ShiftGantt(View):

    #Gantt Charts
    # https://ourcodeworld.com/articles/read/434/top-5-best-free-jquery-and-javascript-dynamic-gantt-charts-for-web-applications
    # https://frappe.io/gantt
    # https://dhtmlx.com/blog/d3-gantt-charts-vs-dhtmlx-gantt/

    @staticmethod
    def funcname(parameter_list):
        pass


    def dispatch_request(self):
        return render_template('gantt_example.html')



class AdminEmployee(MethodView):

    @staticmethod
    def add_new_employee(first_name, last_name, gender, dob, username, email,
        phone, em_contact, em_rel, em_phone, fin_tfn, ea, skills):

        # add employee and skill asignments
        max_employee_id = db.session.query(
            db.func.max(models.Employee.id)).first()[0]

        if max_employee_id == None:
            #if the shift db is empty init the shift id
            max_employee_id = 0
        else:
            max_employee_id += 1

        db.session.add(models.Employee(
            id = max_employee_id,
            username = username,
            email = email, 
            password_hash = new_employee_default_password(username),
            agreement = ea
        ))

        #align employee skills
        max_skill_alignment_id = db.session.query(
            db.func.max(models.SkillAssignment.id)).first()[0]

        if max_skill_alignment_id == None:
            max_skill_alignment_id = 0
        else:
            max_skill_alignment_id += 1

        for skill in skills:
            db.session.add(models.SkillAssignment(
                id = max_skill_alignment_id,
                skill = skill,
                employee = max_employee_id
            ))
            max_skill_alignment_id += 1

        db.session.commit()

        #https://stackoverflow.com/questions/26079754/flask-how-to-return-a-success-status-code-for-ajax-call
        pass

    @staticmethod
    def del_employee(id):

        db.session.query(models.Employee)\
        .filter(models.Employee.id.in_(id))\
        .delete(synchronize_session=False)

        db.session.query(models.SkillAssignment)\
        .filter(models.SkillAssignment.shift.in_(id))\
        .delete(synchronize_session=False)

        db.session.commit()
        pass

    def edit_employee(id, **kwargs):

        emp = db.session.query(models.Employee)\
            .filter(models.Employee.id == id).first()
        emp_skills = db.session.query(models.SkillAssignment)\
            .filter(models.SkillAssignment.employee == id).all()

        # alter the employee specific information
        for kwarg in kwargs:
            if kwarg in ['username','email','password_hash','agreement']:
                setattr(emp, kwarg, kwargs[kwarg])

        # remove, check and add skill asignments where applicable
        if 'skill' in kwargs:
            skills_current = [] 
            for emp_skill in emp_skills:
                if emp_skill.skill not in kwargs['skill']:
                    emp_skill.delete(synchronize_session=False)
                else:
                    skills_current.append(emp_skill.skill)
            

            max_skill_alignment_id = db.session.query(
                db.func.max(models.SkillAssignment.id)).first()[0]

            if max_skill_alignment_id == None:
                max_skill_alignment_id = 0
            else:
                max_skill_alignment_id += 1


            for sk in kwargs['skill']:
                if sk not in skills_current:
                    # add those skills which were missing
                    db.session.add(models.SkillAssignment(
                        id = max_skill_alignment_id,
                        skill = sk,
                        employee = id
                    ))
                    max_skill_alignment_id += 1

        db.session.commit()
                

        pass




    def get(self):


        # get the skills to append to the form
        skills = db.session.query(models.Skill.id, models.Skill.name).all()
        ea = db.session.query(models.EnterpriseAgreement.id, 
            models.EnterpriseAgreement.name).all()
        print(ea)

        return render_template('admin_employee.html' , skills = skills, 
            enterprise_agreement = ea)

    def post(self):

        request_data = request.get_json()
        # test wtforms multidict mapping without html jinja injection

        # Data is correct

        first_name = request_data['addData']["first_name"]
        last_name = request_data['addData']["last_name"]
        gender = request_data['addData']["gender"]
        dob = request_data['addData']["dob"]
        username = request_data['addData']["username"]
        email = request_data['addData']["email"]
        phone =  request_data['addData']["phone"]
        em_contact =  request_data['addData']["em_contact"]
        em_rel =  request_data['addData']["em_rel"]
        em_phone  = request_data['addData']["em_phone"]
        fin_tfn  = request_data['addData']["fin_tfn"]
        ea = request_data['addData']["ea"]
        skills = request_data['addData']["skills"]

        if request_data['postMethod'] == 'add':

            # hook up form validator here "nested_class_test"
            add_validator = nested_class_test(request_data['addData'], 
                {
                    'first_name':[
                        valid.DataRequired('first_name - DataRequired'),
                        valid.Length(1, 26, "first_name - Length")
                        ],
                    'last_name':[
                        valid.DataRequired('last_name - DataRequired'),
                        valid.Length(1, 26, "last_name - Length")
                        ],
                    'gender':[
                        valid.InputRequired('gender - InputRequired'),
                        valid.AnyOf(['Male',"Female"], 'gender - AnyOf')
                    ],
                    'dob':[
                        valid.DataRequired('dob - DataRequired'),
                    ],
                })

            #validate errors - return errors
            if add_validator.validate() == False:
                return json.dumps({'success':False, \
                    'errors':add_validator.errors }), \
                    400, {'ContentType':'application/json'} 

            try:

                # add to database
                self.add_new_employee(first_name, last_name, gender, dob, username, 
                    email, phone, em_contact, em_rel, em_phone, fin_tfn, ea, skills)

                return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

            except:

                return json.dumps({'success':False}), 403, {'ContentType':'application/json'} 

        elif request_data['postMethod'] == 'delete':
            pass
        elif request_data['postMethod'] == 'edit':
            pass

        pass

    pass


class AJAX_AdminEmployeeTable(MethodView):

    def get(self):

        employees =  [list(x) for x in db.session.execute(
            "SELECT id, username, email, agreement FROM employee"
        )]

        return json.jsonify(data = employees)



class CSRFAjax(MethodView):

    decorators = [exclude_from_csrf]

    def get(self):

        if '_csrf_token' not in session:
            token = generate_csrf_token()

            return json.dumps({'success':True, 'token':token}), \
                200, {'ContentType':'application/json'} 

        else:
            return json.dumps({'success':False}), \
                400, {'ContentType':'application/json'}




app.add_url_rule('/index/', view_func=PrimaryView.as_view('index'))
app.add_url_rule('/chart/', view_func=PeriodChart.as_view('period_chart'))
app.add_url_rule('/gantt/', view_func=ShiftGantt.as_view('gantt_chart'))
app.add_url_rule('/login/', view_func=LoginView.as_view('login'))

# Tesst Views
app.add_url_rule('/test_shiftTable/', view_func=AJAX_ShiftTable.as_view('shiftTable'))
app.add_url_rule('/test_shift/', view_func=ShiftTable.as_view('shift'))
app.add_url_rule('/test_shift_delete/', view_func=AJAX_ShiftEdit.as_view('shift_delete'))

# Employee admin Views
app.add_url_rule('/admin_employee/', view_func=AdminEmployee.as_view('adminEmployee'))
app.add_url_rule('/admin_employee_table/', view_func=AJAX_AdminEmployeeTable.as_view('adminEmployeeTable'))


# helper AJAX views
app.add_url_rule('/csrf_ajax/', view_func=CSRFAjax.as_view('csrf_ajax'))