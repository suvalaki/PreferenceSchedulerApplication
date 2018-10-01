# http://flask.pocoo.org/docs/1.0/views/
# https://ourcodeworld.com/articles/read/434/top-5-best-free-jquery-and-javascript-dynamic-gantt-charts-for-web-applications

#https://github.com/wbkd/awesome-d3

from flask import render_template, request, json
from flask.views import View, MethodView
from app import app
from app import db, models
import random
import matplotlib
import matplotlib.cm as cm
from flask.json import jsonify


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


app.add_url_rule('/index/', view_func=PrimaryView.as_view('index'))
app.add_url_rule('/chart/', view_func=PeriodChart.as_view('period_chart'))
app.add_url_rule('/gantt/', view_func=ShiftGantt.as_view('gantt_chart'))
app.add_url_rule('/login/', view_func=LoginView.as_view('login'))

# Tesst Views
app.add_url_rule('/test_shiftTable/', view_func=AJAX_ShiftTable.as_view('shiftTable'))
app.add_url_rule('/test_shift/', view_func=ShiftTable.as_view('shift'))
app.add_url_rule('/test_shift_delete/', view_func=AJAX_ShiftEdit.as_view('shift_delete'))