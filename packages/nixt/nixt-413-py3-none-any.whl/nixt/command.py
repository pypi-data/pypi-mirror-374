# This file is placed in the Public Domain.


"commands"


import inspect


from .handler import Fleet
from .methods import parse, spl


class Commands:

    cmds  = {}
    names = {}

    @staticmethod
    def add(func, module=None) -> None:
        Commands.cmds[func.__name__] = func
        if module:
            Commands.names[func.__name__] = module.__name__.split(".")[-1]

    @staticmethod
    def typed(type):
        result = []
        for name, func in Commands.cmds.items():
            if "types" not in dir(func):
                result.append(name)
                continue
            gotcha = False
            for typ in func.types:
                if typ.lower() in type.lower():
                    gotcha = True
                    break
            if gotcha:
                result.append(name)
        return result                    

    @staticmethod
    def get(cmd):
        return Commands.cmds.get(cmd, None)


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in cmdz.__code__.co_varnames:
            Commands.add(cmdz, module)


def __dir__():
    return (
        'Commands',
        'command',
        'scan'
    )
