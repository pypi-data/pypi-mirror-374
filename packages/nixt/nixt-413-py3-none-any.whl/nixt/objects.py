# This file is placed in the Public Domain.


"a clean namespace"


import json


class Object:

    def __contains__(self, key):
        return key in dir(self)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        if isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        elif isinstance(val, Object):
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)


def edit(obj, setter, skip=True):
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


def fmt(obj, args=None, skip=None, plain=False, empty=False, newline=False):
    if args is None:
        args = keys(obj)
    if skip is None:
        skip = []
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if not empty and not value:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str):
            txt += f'{key}="{value}" '
        else:
            txt += f"{key}={value} "
        if newline:
            txt += "\n"
    return txt.strip()


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def items(obj):
    if isinstance(obj, dict):
        return obj.items()
    return obj.__dict__.items()


def keys(obj):
    if isinstance(obj, dict):
        return obj.keys()
    return obj.__dict__.keys()


def search(obj, selector, matching=False):
    res = False
    if not selector:
        return res
    for key, value in items(selector):
        val = getattr(obj, key, None)
        if not val:
            continue
        if matching and value == val:
            res = True
        elif str(value).lower() in str(val).lower() or value == "match":
            res = True
        else:
            res = False
            break
    return res


def update(obj, data):
    for key, value in items(data):
        if key and value:
            setattr(obj, key, value)


def values(obj):
    if isinstance(obj, dict):
        return obj.values()
    return obj.__dict__.values()


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if issubclass(type(o), Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dump(obj, fp, *args, **kw):
    kw["cls"] = Encoder
    json.dump(obj, fp, *args, **kw)


def dumps(obj, *args, **kw):
    kw["cls"] = Encoder
    return json.dumps(obj, *args, **kw)


def hook(objdict):
    obj = Object()
    construct(obj, objdict)
    return obj


def load(fp, *args, **kw):
    kw["object_hook"] = hook
    return json.load(fp, *args, **kw)


def loads(s, *args, **kw):
    kw["object_hook"] = hook
    return json.loads(s, *args, **kw)


def __dir__():
    return (
        'Object',
        'construct',
        'dump',
        'dumps',
        'edit',
        'fmt'
        'fqn',
        'items',
        'keys',
        'load',
        'loads',
        'search',
        'update',
        'values'
    )
