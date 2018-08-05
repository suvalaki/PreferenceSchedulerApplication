# http://flask.pocoo.org/docs/1.0/views/
# https://ourcodeworld.com/articles/read/434/top-5-best-free-jquery-and-javascript-dynamic-gantt-charts-for-web-applications

#https://github.com/wbkd/awesome-d3

from flask import render_template, json
from flask.views import View, MethodView
from app import app
from app import db, models
import random
import json
import matplotlib
import matplotlib.cm as cm

def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)


class LoginView(View):

    


    def dispatch_request(self):
        return 1

class PrimaryView(View):

    def dispatch_request(self):
        return render_template('index.html' )

class PeriodChart(View):

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


class ShiftGantt(View):

    #Gantt Charts
    # https://ourcodeworld.com/articles/read/434/top-5-best-free-jquery-and-javascript-dynamic-gantt-charts-for-web-applications
    # https://frappe.io/gantt
    # https://dhtmlx.com/blog/d3-gantt-charts-vs-dhtmlx-gantt/


    def dispatch_request(self):
        return render_template('gantt_example.html')


app.add_url_rule('/index/', view_func=PrimaryView.as_view('index'))
app.add_url_rule('/chart/', view_func=PeriodChart.as_view('period_chart'))
app.add_url_rule('/gantt/', view_func=ShiftGantt.as_view('gantt_chart'))