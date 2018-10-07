# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 17:27:37 2018

Two different ways of producing flask_input validator classes (func and class).

The idea is to use WTForms validators to validate json data which has been 
returned as a dictionairy. 

Flask_Input expected data to be passed to it as dictionairies from a flask 
request type. to get around this we define a class with an interior attribute
'value' (instead of response.value) and make our tests against that. 

Tghe first method provides a function for dynamic creation of a class at 
runtime from functional inputs

the second method creates the ruleset beforehand as a class and customises an
input initialisatiosn function. The second methtod places the valdiatior 
functions supplied by flask_input within the 'validator' attribute

@author: david
"""

from flask_inputs import Inputs
from wtforms.validators import DataRequired
from werkzeug.datastructures import MultiDict

def nested_class_test(json_dict, value_rule_dict):

    class inner_value_class:
        def __init__(self, json_dict):
            self.values = MultiDict(mapping = json_dict)

    class inner_rule_class(Inputs):
        values = value_rule_dict

    return inner_rule_class(inner_value_class(json_dict))


test_case_true = nested_class_test({'username':'david'},
                              {'username': [DataRequired(),]})
test_case_true.validate()

test_case_false = nested_class_test({'username':None},
                              {'username': [DataRequired(),]})
test_case_false.validate()



# Class based version of the same


class nested_class_testclass:

    def __init__(self, json_dict):
        self.values = MultiDict(mapping = json_dict)
        self.validator = self.inner_rule_class(self)

    class inner_rule_class(Inputs):

        values = {
                # rules go here
                'username':[DataRequired(),]
                }
        
test_true = nested_class_testclass({'username':'david'})
test_true.validator.validate()

test_false = nested_class_testclass({'username':None})
test_false.validator.validate()
