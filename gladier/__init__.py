from inspect import getmembers, isclass
import importlib
import logging

# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library  # noqa
logging.getLogger("gladier").addHandler(logging.NullHandler())


from gladier.base import * 

## Dynamic import GladierBase*
base_mod = importlib.import_module('gladier.base')
base_classes = getmembers(base_mod, isclass)

__all__=[]

for k in base_classes:
    __all__.append(k[0])


print("Starting Gladier Library with following GladierBaseClasses")
print(__all__)

