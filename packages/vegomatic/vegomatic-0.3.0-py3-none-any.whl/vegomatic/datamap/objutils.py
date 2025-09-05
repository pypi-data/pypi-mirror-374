#
# objutils - Various object utilities.
#

from collections import namedtuple
from types import SimpleNamespace
from copy import copy
import inspect
from numbers import Number

def ikeyval(inkey):
    keyval = inkey
    if is_number(inkey) and inkey > 1000000000:
        keyval = str(inkey)
    return keyval

def fixedobj_from_dict(aname: str, indict: dict, normalize=True) -> object:
    adict = copy(indict)
    if normalize:
        for key, val in adict.items():
            adict[ikeyval(key)] = normalize_value(val)
    retobj  = namedtuple(aname, adict.keys())(*adict.values())
    return retobj


def dict_from_object(anobj: object, fieldlist=None, missing=None) -> dict:
    retdict = {}
    if fieldlist is None:
        fieldlist = anobj.__dict__.keys()
    for fname in fieldlist:
        fval = getattr(anobj, fname, missing)
        retdict[fname] = fval
    return retdict


def dynobj_from_dict(indict: dict, normalize=True) -> object:
    adict = copy(indict)
    if normalize:
        for key, val in adict.items():
            adict[ikeyval(key)] = normalize_value(val)
    retobj  = SimpleNamespace()
    for key, val in adict.items():
        setattr(retobj, ikeyval(key), val)
    return retobj


def objlist_from_dictlist(aname: str, alist: list) -> list:
    retlist = []
    for ditem in alist:
        oitem = dynobj_from_dict(ditem)
        retlist.append(oitem)
    return retlist


def getvalue(anitem: dict | object, keyprop:str):
    if inspect.isclass(type(anitem)):
        keyval = getattr(anitem, keyprop, None)
    elif type(anitem) == dict:
        if keyprop == dict:
            keyval = anitem[keyprop]
        else:
            keyval = None
    else:
        raise TypeError
    return keyval


def dict_from_list(alist: list, keyprop: str, ignore_missing_key=True) -> dict:
    retdict = {}
    for anitem in alist:
        keyval = getvalue(anitem, keyprop)
        if keyval is None:
            if not ignore_missing_key:
                raise KeyError
            else:
                continue
        # Force key to string if it looks like a really big int - fudge for UUID/TXND type keys
        keyval = ikeyval(keyval)
        retdict[keyval] = anitem
    return retdict


def list_find_by_prop(alist: list, propname: str, propval: str | int | float):
    for item in alist:
        if propname not in item:
            continue
        if item[propname] == propval:
            return item
    return None


def is_number(s: None | str) -> bool:
    if s is None:
        return False
    nval = num_value(s)
    if isinstance(nval, (float,int)):
        return True
    return False


def num_value(s:str) -> None | float | int:
    nval = normalize_value(s)
    if isinstance(nval, (float,int)):
        return nval
    return None

# Normalize simple values to integral int or float type if possible
def normalize_value(s: None | str) -> None | float | int | str:
    if isinstance(s, (None,dict,list,object)):
        return None

    try:
        nval = int(s)
        if nval.is_integer():
            return nval
    except ValueError:
        pass

    try:
        nval = float(s)
        return nval
    except ValueError:
        pass

    return s

# Return a new list sorted by the keylist from a dict
def sort_list(adict: dict, keyseq: list[str]) -> list:
    return sorted(adict, key=lambda x: [x[key] for key in keyseq])


def flatten_to_dict(nested_obj: dict, separator: str = "_") -> dict:
    """
    Flatten a nested dictionary by joining keys with a separator.

    Args:
        nested_obj: The nested dictionary to flatten
        separator: The separator to use when joining keys (default: "_")

    Returns:
        A flattened dictionary with single-level keys

    Example:
        Input: {"level1": {"level2": "value"}}
        Output: {"level1_level2": "value"}
    """
    flattened = {}

    def _flatten(obj, prefix=""):
        if not isinstance(obj, dict):
            return

        for key, value in obj.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                _flatten(value, new_key)
            elif isinstance(value, (Number,str,bool,bytes,bytearray)):
                # Only include integral types
                flattened[new_key] = value
            elif isinstance(value, (list, tuple, range, set, frozenset, memoryview)):
                # Lists and other "complex" objects are ignored as per requirements
                pass
            else:
                # Other objects are ignored as per requirements
                pass

    _flatten(nested_obj)
    return flattened

