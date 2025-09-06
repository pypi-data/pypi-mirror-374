# This file is placed in the Public Domain.


"modules"


import os


path = os.path.dirname(__file__)


def modules(path):
    return sorted([
            x[:-3] for x in os.listdir(path)
            if x.endswith(".py") and not x.startswith("__")
           ])


"interface"


def __dir__():
    return modules(path)
