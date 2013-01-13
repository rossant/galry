import sys
import os
import inspect
import imp
import operator
import pprint

import galry

def get_function_doc(fun):
    return inspect.getdoc(fun)

def get_class_doc(cls):
    methods = inspect.getmembers(cls, inspect.ismethod)
    return dict([(name, get_function_doc(value)) for name, value in dict(methods).iteritems()])
    

members = dict(inspect.getmembers(galry))
classes = filter(inspect.isclass, members.values())

# for cls in classes:
    # print cls, inspect.getdoc(cls)

pprint.pprint(get_class_doc(classes[0]))

# print classes


