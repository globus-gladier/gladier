from os.path import dirname, basename, isfile, join
from inspect import getmembers, isfunction
import importlib
import glob
import logging

# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library  # noqa
logging.getLogger("gladier").addHandler(logging.NullHandler())

funcs=[]
base_mod = importlib.import_module('gladier.base')
mod_functions = getmembers(base_mod, isfunction)
for f in mod_functions:
    funcs.append(+f[0])

__all__ = funcs
