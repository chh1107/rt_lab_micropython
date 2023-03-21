# Based on https://github.com/micropython-IMU/micropython-fusion

# Original Header:
# Sensor fusion for the micropython board. 25th June 2015
# Ported to MicroPython by Peter Hinch.
# Released under the MIT License (MIT)
# Copyright (c) 2017, 2018 Peter Hinch

from math import sqrt, atan2, asin, degrees, radians
from lab.deltat import DeltaT

class GyroMadgwick(object):
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

    def run(self, gyro_obj, iterations=0, infinite=True):
        while infinite or iterations > 0:
            gyro_mdps = (v / 1000.0 for v in gyro_obj.get_xyz())
            self.update(gyro_mdps)
            if not infinite:
                iterations -= 1
            yield self.pitch, self.roll


def main():
    import gyro as g
    g.init()
    gm = GyroMadgwick()

    from lab import display_tools
    d = display_tools.Display()
    w, h = d.width(), d.height()

    import lvgl as lv
    c_w, c_h = int(w * 0.5), h
    b_w, b_h = int(w * 0.1), int(h * 0.8)
    col_dsc = [c_w, c_w, lv.GRID_TEMPLATE_LAST]
    row_dsc = [c_h, c_h, lv.GRID_TEMPLATE_LAST]

    # Create a container with grid
    cont = lv.obj(lv.scr_act())
    cont.set_style_grid_column_dsc_array(col_dsc, 0)
    cont.set_style_grid_row_dsc_array(row_dsc, 0)
    cont.set_size(w, h)
    cont.center()
    cont.set_layout(lv.LAYOUT_GRID.value)

    bar1 = lv.bar(cont)
    bar1.set_size(b_w, b_h)
    bar1.align(lv.ALIGN.CENTER, 0, 0)
    bar1.set_range(-90, 90)
    bar1.set_value(0, lv.ANIM.OFF)
    bar1.set_grid_cell(lv.GRID_ALIGN.CENTER, 0, 1,
                       lv.GRID_ALIGN.CENTER, 0, 1)

    bar2 = lv.bar(cont)
    bar2.set_size(b_w, b_h)
    bar2.align(lv.ALIGN.CENTER, 0, 0)
    bar2.set_range(-90, 90)
    bar2.set_value(0, lv.ANIM.OFF)
    bar2.set_grid_cell(lv.GRID_ALIGN.CENTER, 1, 1,
                       lv.GRID_ALIGN.CENTER, 0, 1)

    for pitch, roll in gm.run(g):
        bar1.set_value(int(pitch), lv.ANIM.OFF)
        bar2.set_value(int(roll), lv.ANIM.OFF)
