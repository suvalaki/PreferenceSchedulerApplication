import cvxpy as cp
import numpy as np
from app.models import *
from app import db
import pulp

# Formulating the nurse problem

# For each shift we need

# Get Roles
roles = np.asarray([ role[0] for role in db.session.execute(
    "SELECT DISTINCT requirement from schedule_requirement ORDER BY id")])

# GET Periods
periods = np.asarray([ p[0] for p in db.session.execute(
    "SELECT DISTINCT id from period ORDER BY id")])

##### Get requirement of personel to each period
role_requirements = np.array([[e_i[0] for e_i in 
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

#Get Shifts
shifts = np.asarray([x[0] for x in db.session.execute(
    """
    SELECT DISTINCT id
    FROM shift
    ORDER BY id
    """
)])

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



# Optimisation

# Variable. Assign each 
allocations = pulp.LpVariable.dicts("A",((e,s,p,a) 
    for e in employees 
    for s in shifts
    for p in periods
    for a in roles),
    0,1,cat='Binary')

# Contraints
#https://www.programcreek.com/python/example/96869/cvxpy.sum_entries
# https://wiki.python.org/moin/PythonForOperationsResearch
# https://www.coin-or.org/PuLP/pulp.html#pulp.LpConstraint
# pulp puts in the constraint automatically
# http://benalexkeen.com/linear-programming-with-python-and-pulp-part-4/
# https://medium.freecodecamp.org/python-list-comprehensions-vs-generator-expressions-cef70ccb49db

# Contraint that an employee can only occupy a single point in time. 
employee_single_period_assignment = (pulp.LpAffineExpression(
            ((allocations[emp, s, p, a],1) 
            for s in shifts
            for a in roles) <= 1
        for p in periods)
    for emp in employees) 

# Employee can only perform a skill for which they have the capability
employee_has_capability = (pulp.LpAffineExpression(
    ((allocations[emp, s, p, a],1)) ) <= employee_skill_identifier[a , emp] 
    for s in range(len(shifts))
    for a in range(len(roles))
    for p in range(len(periods))
    for emp in range(len(employees)) )

# During each period the role requirements must be met
period_role_requirement = (pulp.LpAffineExpression(
    ((allocations[emp,s,p,a],1)
    for emp in employees
    for s in shifts ) >= 
))