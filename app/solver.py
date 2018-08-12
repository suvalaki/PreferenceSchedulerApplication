
import sqlalchemy as sql
import sqlalchemy.orm as orm
import numpy as np
import pulp

from app import db
from app.models import ScheduleAllocation

"""
class db:
    pass

db_uri = 'sqlite:///C:\\Users\\david\\Documents\\GitHub\\PreferenceSchedulerApplication\\app\\app.db'
db.engine = sql.create_engine(db_uri)
db.Session = orm.session.sessionmaker()
db.Session.configure(bind=db.engine)
db.session = db.Session()

"""

def list_index_mapping(lis):
    index = 0
    mapping = dict()
    for li in lis:
        mapping[str(li)] = index
        index += 1
    return mapping


# Get Roles
roles = np.asarray([ role[0] for role in db.session.execute(
    "SELECT DISTINCT requirement from schedule_requirement ORDER BY id")])
    
roles_index = list_index_mapping(roles)

# GET Periods
periods = np.asarray([ p[0] for p in db.session.execute(
    "SELECT DISTINCT id from period ORDER BY id")])
    
periods_index = list_index_mapping(periods)

##### Get requirement of personel to each period
role_requirements = np.array([[e_i[0] for e_i in 
    db.session.execute(
        """
        SELECT COUNT(id) 
        FROM schedule_requirement
        WHERE requirement=:param
        GROUP BY period
        ORDER BY period
        """,
        {"param": str(x)}
    )
] for x in roles ]) # [periods, roles]

#Get Shifts
shifts = np.asarray([x[0] for x in db.session.execute(
    """
    SELECT DISTINCT id
    FROM shift
    ORDER BY id
    """
)])
    
shifts_index = list_index_mapping(shifts)


#Get Shifts allocation to periods
shift_period_identifier = np.asarray( [[y[0] for y in db.session.execute(
    """
    SELECT 
        CASE WHEN shift =:param THEN 1 ELSE 0 END AS col 
    FROM period
    LEFT OUTER JOIN (
        SELECT period, shift
        FROM shift_periods
        WHERE shift =:param
        ORDER BY period
        ) as s_p
    ON period.id = s_p.period
    ORDER BY id
    """,
        {"param": str(x)}
    )
] for x in shifts ])


# Get employees
employees = np.array([x[0] for x in 
    db.session.execute("""
    SELECT id FROM employee
    ORDER BY id
    """)])
    
employees_index = list_index_mapping(employees)

# Get capability of employees to each required role
employee_skill_identifier = np.array([[e_i[0] for e_i in 
    db.session.execute(
        """
        SELECT CASE WHEN skill =:param then 1 else 0 END as col
        FROM (
            SELECT employee.id as id2, emp, skill
            FROM employee
            LEFT OUTER JOIN (
                SELECT employee as emp, skill
                FROM skill_assignment
                WHERE skill =:param
            ) as skill_slice
            ON employee.id = skill_slice.emp
        ) as employee_skill_slice
        ORDER BY id2
                """,
        {"param": str(x)}
    )
] for x in roles ])


# Get enterprise agreements
enterprise_agreements = np.asarray([ ea[0] for ea in db.session.execute(
    "SELECT DISTINCT id from enterpriseagreement ORDER BY id")])
    
enterprise_agreements = list_index_mapping(enterprise_agreements)

#get whether an employee has an enterprise agreement
emplyee_ea_identifier = np.array([[ea_e[0] for ea_e in 
    db.session.execute(
        """
        SELECT 
            CASE 
                WHEN agreement =:param THEN 1 ELSE 0 END AS ea_i
        FROM employee
        ORDER BY id
        """,
        {"param": str(x)}
    )
] for x in enterprise_agreements ])

#Get Wages per enterprise agreement
enterprise_agreement_wage = np.array([ 
    db.session.execute(
        """
        SELECT DISTINCT wage
        FROM enterpriseagreement
        WHERE id =:param
        ORDER BY id
        """,
        {"param": str(x)}
    ).fetchone()[0]
 for x in enterprise_agreements ])

#Get Overtime Wages per enterprise agreement
enterprise_agreement_wage_overtime = np.array([ 
    db.session.execute(
        """
        SELECT DISTINCT wage_overtime
        FROM enterpriseagreement
        WHERE id =:param
        ORDER BY id
        """,
        {"param": str(x)}
    ).fetchone()[0]
 for x in enterprise_agreements ])

#Get Min normal hours per enterprise agreement
enterprise_agreement_min_periods = np.array([ 
    db.session.execute(
        """
        SELECT DISTINCT min_periods
        FROM enterpriseagreement
        WHERE id =:param
        ORDER BY id
        """,
        {"param": str(x)}
    ).fetchone()[0]
 for x in enterprise_agreements ])

#Get Max normal hours per enterprise_agreement
enterprise_agreement_max_periods = np.array([ 
    db.session.execute(
        """
        SELECT DISTINCT max_periods
        FROM enterpriseagreement
        WHERE id =:param
        ORDER BY id
        """,
        {"param": str(x)}
    ).fetchone()[0]
 for x in enterprise_agreements ])

#Get Max ovetime hours per enterprise_agreemnet
enterprise_agreement_max_periods_overtime = np.array([ 
    db.session.execute(
        """
        SELECT DISTINCT max_periods_overtime
        FROM enterpriseagreement
        WHERE id =:param
        ORDER BY id
        """,
        {"param": str(x)}
    ).fetchone()[0]
 for x in enterprise_agreements ])

#Get weeks
weeks = np.array([ x[0] for x in
    db.session.execute(
        """
        SELECT DISTINCT week
        FROM period
        ORDER BY id
        """
    )])
    
weeks_index = list_index_mapping(weeks)

#Get wekk allocations (the period cycle under which max times reset)
week_identifier = np.array([[week_i[0] for week_i in 
    db.session.execute(
        """
        SELECT 
            CASE 
                WHEN week =:param THEN 1 ELSE 0 END AS week_i
        FROM period
        ORDER BY id
        """,
        {"param": str(x)}
    )
] for x in weeks ])

# Get the objective constants

# get the preferences of each employee to each shift



# Optimisation

def admissible_index(e,s,p,a):
    # used to reduce the number of objects made to only be useful.
    # dramatically reduces memory usage
    return employee_skill_identifier[roles_index[str(a)],
                                    employees_index[str(e)]] and \
            shift_period_identifier[shifts_index[str(s)],
                                    periods_index[str(p)]]

def admissible_role(e,a):
    return employee_skill_identifier[roles_index[str(a)],
                                    employees_index[str(e)]]


# Variable. Assign each 
allocations = pulp.LpVariable.dicts("A",((e,s,p,a) 
    if admissible_index(e,s,p,a) else None
    for e in employees 
    for s in shifts
    for p in periods
    for a in roles),
    0,1,cat='Integer')

# Normal work hour assignments
allocations_normal = pulp.LpVariable.dicts("A_n",((e,s,p,a) 
    if admissible_index(e,s,p,a) else None
    for e in employees 
    for s in shifts
    for p in periods
    for a in roles),
    0,1,pulp.LpBinary)

# Overtime work hour assignments
allocations_overtime = pulp.LpVariable.dicts("A_o",((e,s,p,a) 
    if admissible_index(e,s,p,a) else None
    for e in employees 
    for s in shifts
    for p in periods
    for a in roles),
    0,1,pulp.LpBinary)

shift_allocations = pulp.LpVariable.dicts("S",((e,s,a) 
    if admissible_role(e,a) else None
    for e in employees 
    for s in shifts
    for a in roles),
    0,1,pulp.LpBinary)


# Contraints
#https://www.programcreek.com/python/example/96869/cvxpy.sum_entries
# https://wiki.python.org/moin/PythonForOperationsResearch
# https://www.coin-or.org/PuLP/pulp.html#pulp.LpConstraint
# pulp puts in the constraint automatically
# http://benalexkeen.com/linear-programming-with-python-and-pulp-part-4/
# https://medium.freecodecamp.org/python-list-comprehensions-vs-generator-expressions-cef70ccb49db

# MAY BE ABLE TO OPTIMISE MEMORY BY TRUNCATING PERIODS TO THE SPECIFIC SHIFT


# Contraint that an employee can only occupy a single point in time. 
employee_single_period_assignment = [pulp.LpAffineExpression(
            ((allocations[emp, s, p, a],1) 
            for s in shifts
            for a in roles
            if admissible_index(emp,s,p,a))) <= 1
        for p in periods
        for emp in employees
]


# shifts enforced by periods
shift_assignemnt_constraint = [shift_allocations[emp,s,a] == \
        allocations[emp,s,p,a] 
        for emp in  employees
        for s in shifts
        for p in periods
        for a in roles
        if admissible_index(emp,s,p,a) ]

#E Employee single skkill per shift assignment
single_role_per_shift_constraint = [pulp.LpAffineExpression(
    ((shift_allocations[emp,s,a] ,1)
    for a in roles
    if admissible_role(emp,a)))<=1
    for emp in employees
    for s in shifts
]



# Employee can only perform a skill for which they have the capability
# employee capability is actually implicit when using addmissible_index
employee_has_capability = [
    allocations[emp, s, p, a] <= 
        employee_skill_identifier[roles_index[str(a)], 
                                employees_index[str(emp)]] 
    for s in shifts
    for a in roles
    for p in periods
    for emp in employees 
    if admissible_index(emp,s,p,a)
]

# During each period the role requirements must be met
period_role_requirement = [pulp.LpAffineExpression((
    (allocations[emp,s,p,a], shift_period_identifier[shifts_index[str(s)],
                                                     periods_index[str(p)]] )
    for emp in employees
    for s in shifts 
    if admissible_index(emp,s,p,a)
    )) >= role_requirements[roles_index[str(a)],
                                            periods_index[str(p)]] 
    for p in periods
    for a in roles
]


# Contraint that an employee can only be working normal or overtime but not both
single_normal_overtime = (
    allocations_normal[emp, s, p, a] + allocations_overtime[emp, s, p, a] == 
    allocations[emp, s, p, a]
    for emp in employees 
    for s in shifts         
    for p in periods
    for a in roles
    if admissible_index(emp,s,p,a)
)


# minimum normal working hours
min_normal_hours = (pulp.LpAffineExpression(
    (allocations_normal[emp, s, p, a],1)
    for s in shifts
    for p in periods 
    for a in roles 
    if admissible_index(emp,s,p,a)
    ) >= enterprise_agreement_min_periods[
        emplyee_ea_identifier[:,employees_index[str(emp)]] == 1] 
    for emp in employees
)



# maximum amount of normal working hours
max_normal_hours = (pulp.LpAffineExpression(
    (allocations_normal[emp, s, p, a],1) 
    for s in shifts
    for p in periods
    for a in roles 
    if admissible_index(emp,s,p,a)
    ) <= enterprise_agreement_max_periods[
        emplyee_ea_identifier[:,employees_index[str(emp)]] == 1] 
    for emp in employees
)


# Employee can only work overtime hours when they have maxed out normal working 
# hours
employee_normal_working_hours_before_overtime = (
    allocations_overtime[emp, s, p, a]
    <= pulp.LpAffineExpression(
        (allocations_normal[emp, s1, p1, a1],1)       
        for s1 in shifts
        for p1 in periods
        for a1 in roles
        if admissible_index(emp,s1,p1,a1)
    ) / enterprise_agreement_max_periods[
            emplyee_ea_identifier[:,employees_index[str(emp)]] == 1] 
    for s in shifts
    for p in periods
    for a in roles
    for emp in employees
    if admissible_index(emp,s,p,a)
)


# Objective function. The sum of costs
obj = pulp.lpSum(
    allocations_normal[emp, s, p, a] * enterprise_agreement_wage[
        emplyee_ea_identifier[:,employees_index[str(emp)]] == 1] +\
    allocations_overtime[emp, s, p, a] * enterprise_agreement_wage_overtime[
        emplyee_ea_identifier[:,employees_index[str(emp)]] == 1] 
    for emp in employees
    for s in shifts
    for p in periods
    for a in roles
    if admissible_index(emp,s,p,a)
)

# Linear Program
prob =  pulp.LpProblem("My LP Problem", pulp.LpMinimize)
prob += obj

"""

for constraint in employee_single_period_assignment:
    prob += constraint

for constraint in employee_has_capability:
    prob += constraint

for constraint in period_role_requirement:
    prob += constraint

for constraint in single_normal_overtime:
    prob += constraint

for constraint in min_normal_hours:
    prob += constraint

for constraint in max_normal_hours:
    prob += constraint

#for constraint in employee_normal_working_hours_before_overtime:
#    prob += constraint

"""
constraint_set = [
    employee_single_period_assignment,
    shift_assignemnt_constraint,
    single_role_per_shift_constraint,
    employee_has_capability,
    #period_role_requirement,
    single_normal_overtime,
    min_normal_hours,
    max_normal_hours,
    #employee_normal_working_hours_before_overtime
]

for constraints in constraint_set:
    for constraint in constraints:
        prob += constraint
        #print(constraint)


prob.solve()


pulp.LpStatus[prob.status]
prob.objective.value()
#prob.variables()

varsdict = {}

for v in prob.variables():
    varsdict[v.name] = v.varValue
    

for x in prob.variables():
    print("Name:       ", x.name, " Cat: ", x.cat, " Val: ", x.value())

    
#employee_shift_assignmnet = np.zeros((len(employees),len(shifts)))

def update_shift_allocation(allocations, allocations_nor, allocations_ovr):
    
    db.session.execute("DELETE FROM schedule_allocation")
    db.session.commit()
    
    increment = 0
    
    for e in employees:
        for s in shifts:
            for p in periods:
                for a in roles:
                    if admissible_index(e,s,p,a) and allocations[e,s,p,a].value == 1:
                        

                        db.session.add(ScheduleAllocation(
                            id = increment,
                            employee = int(e),
                            shift = int(s),
                            skills = int(a),
                            is_overtime = allocations_ovr[e,s,p,a].varValue == 1
                        ))
                        increment += 1
    
    db.session.commit()
    

update_shift_allocation(allocations,allocations_normal,allocations_overtime)