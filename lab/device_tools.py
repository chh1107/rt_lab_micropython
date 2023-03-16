import os
import machine

def reboot():
    os.sync()
    machine.reset()
