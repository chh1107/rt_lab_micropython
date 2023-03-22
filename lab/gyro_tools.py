# Based on https://github.com/micropython-IMU/micropython-fusion

# Original Header:
# Sensor fusion for the micropython board. 25th June 2015
# Ported to MicroPython by Peter Hinch.
# Released under the MIT License (MIT)
# Copyright (c) 2017, 2018 Peter Hinch

from math import sqrt, atan2, asin, degrees, radians

import stm32f429disc_gyro

from lab.deltat import DeltaT
from lab.device_tools import _getinstance


def get_gyro():
    return _getinstance(Gyro)


class Gyro:
    '''
    Simple wrapper class for the low level gyro driver module
    '''
    def __init__(self):
        stm32f429disc_gyro.init()

    def read_xyz(self):
        return stm32f429disc_gyro.read_xyz()


class GyroMadgwick:
    '''
    Class provides sensor fusion allowing heading, pitch and roll to be extracted. This uses the Madgwick algorithm.
    The update method must be called peiodically. The calculations take 1.6mS on the Pyboard.
    '''
    declination = 0                         # Optional offset for true north. A +ve value adds to heading
    def __init__(self):
        self.deltat = DeltaT(None)          # Time between updates
        self.q = [1.0, 0.0, 0.0, 0.0]       # vector to hold quaternion
        self.pitch = 0
        self.heading = 0
        self.roll = 0

    def update(self, gyro_dps):
        gx, gy, gz = (radians(v) for v in gyro_dps) # Units deg/s
        q1, q2, q3, q4 = (self.q[i] for i in range(4))   # short name local variable for readability

        # Compute rate of change of quaternion
        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) # - self.beta * s1
        qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) # - self.beta * s2
        qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) # - self.beta * s3
        qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) # - self.beta * s4

        # Integrate to yield quaternion
        deltat = self.deltat(None)
        q1 += qDot1 * deltat
        q2 += qDot2 * deltat
        q3 += qDot3 * deltat
        q4 += qDot4 * deltat
        norm = 1 / sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)    # normalise quaternion
        self.q = q1 * norm, q2 * norm, q3 * norm, q4 * norm
        self.heading = 0
        self.pitch = degrees(-asin(2.0 * (self.q[1] * self.q[3] - self.q[0] * self.q[2])))
        self.roll = degrees(atan2(2.0 * (self.q[0] * self.q[1] + self.q[2] * self.q[3]),
            self.q[0] * self.q[0] - self.q[1] * self.q[1] - self.q[2] * self.q[2] + self.q[3] * self.q[3]))

    def run(self, gyro_obj=None, iterations=0, infinite=True):
        if gyro_obj is None:
            gyro_obj = get_gyro()
        while infinite or iterations > 0:
            gyro_mdps = (v / 1000.0 for v in gyro_obj.read_xyz())
            self.update(gyro_mdps)
            if not infinite:
                iterations -= 1
            yield self.pitch, self.roll
