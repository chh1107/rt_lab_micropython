import os
import machine

_instances = {}
def _getinstance(class_, *args, **kwargs):
    if class_ not in _instances:
        _instances[class_] = class_(*args, **kwargs)
    return _instances[class_]

def reboot():
    os.sync()
    machine.reset()
