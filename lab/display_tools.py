# Based on the work by Thomas Hornschuh (https://github.com/ThomasHornschuh)

import lvgl as lv
from lv_utils import event_loop
import stm32f429disc_disp


_instances = {}
def _getinstance(class_, *args, **kwargs):
    if class_ not in _instances:
        _instances[class_] = class_(*args, **kwargs)
    return _instances[class_]

def get_display(calibration_values=[-3, 16, 247, 337]):
    return _getinstance(Display, calibration_values=calibration_values)


class Display:

    def __init__(self, calibration_values=None):
        lv.init()
        stm32f429disc_disp.init()
        self.w = stm32f429disc_disp.lcd_width()
        self.h = stm32f429disc_disp.lcd_height()

        draw_buf = lv.disp_draw_buf_t()
        bufsz =  self.w * 30 * lv.color_t.__SIZE__
        buf1_1 = bytearray(bufsz)
        buf1_2 = bytearray(bufsz)

        draw_buf.init(buf1_1, buf1_2, len(buf1_1) // lv.color_t.__SIZE__)
        disp_drv = lv.disp_drv_t()
        disp_drv.init()
        disp_drv.draw_buf = draw_buf
        disp_drv.flush_cb = stm32f429disc_disp.flush
        disp_drv.hor_res = self.w
        disp_drv.ver_res = self.h
        disp_drv.register()

        indev_drv = lv.indev_drv_t()
        indev_drv.init()
        indev_drv.type = lv.INDEV_TYPE.POINTER
        indev_drv.read_cb = stm32f429disc_disp.ts_read
        indev_drv.register()

        if calibration_values is not None:
            self.set_touchscreen_calibration_values(*calibration_values)

        try:
            event_loop()
        except:
            pass

    def __del__(self):
        stm32f429disc_disp.deinit()

    def width(self):
        return self.w

    def height(self):
        return self.h

    def calibrate_touchscreen(self):
        calibration_points = [
            Calibration_Point(20,  20, 'upper left-hand corner'),
            Calibration_Point(-40, -40, 'lower right-hand corner')
        ]
        calibration_gui = Calibration_GUI(self, calibration_points)
        calibration_gui.begin_calibration()

    def set_touchscreen_calibration_values(self, x1, y1, x2, y2):
        stm32f429disc_disp.ts_calibrate(x1=x1, y1=y1, x2=x2, y2=y2)


# Point class holding display and touch coordiantes
class Calibration_Point():

    def __init__(self, x, y, name):
        self.display_coordinates = lv.point_t({'x': x, 'y': y})
        self.touch_coordinate = None
        self.name = name

    def __repr__(self):
        return f'{self.name}: ({self.touch_coordinate.x}, {self.touch_coordinate.y})'


# Creates a screen with a button and a label
class Calibration_GUI():

    CIRCLE_SIZE = const(20)
    CIRCLE_OFFSET = const(20)
    TP_MAX_VALUE = const(10000)

    LV_COORD_MAX = const((1 << (8 * 2 - 1)) - 1000)
    LV_RADIUS_CIRCLE = const(LV_COORD_MAX) # TODO use lv.RADIUS_CIRCLE constant when it's available!

    def __init__(self, display, points, touch_count=5):
        self.display = display
        self.points = points
        self.touch_count = touch_count

        self.med = [lv.point_t() for i in range(0,self.touch_count)] # Storage point to calculate median

        self.cur_point = 0
        self.cur_touch = 0

        self.scr = lv.obj(None)
        self.scr.set_size(self.display.width(), self.display.height())
        lv.scr_load(self.scr)

    def begin_calibration(self):
        # Create a big transparent button screen to receive clicks
        style_transp = lv.style_t()
        style_transp.init()
        style_transp.set_bg_opa(lv.OPA.TRANSP)
        self.big_btn = lv.btn(lv.scr_act())
        self.big_btn.set_size(self.display.width(), self.display.height())
        self.big_btn.add_style(style_transp, lv.PART.MAIN)
        self.big_btn.add_style(style_transp, lv.PART.MAIN)
        #self.big_btn.set_layout(lv.LAYOUT.OFF)
        self.big_btn.add_event_cb(lambda event, self=self: self._calibrate_clicked(event), lv.EVENT.CLICKED, None)

        # Create the screen, circle and label
        self.label_main = lv.label(lv.scr_act())
        style_circ = lv.style_t()
        style_circ.init()
        style_circ.set_radius(Calibration_GUI.LV_RADIUS_CIRCLE)
        self.circ_area = lv.obj(lv.scr_act())
        self.circ_area.set_size(Calibration_GUI.CIRCLE_SIZE, Calibration_GUI.CIRCLE_SIZE)
        self.circ_area.add_style(style_circ, lv.STATE.DEFAULT)
        self.circ_area.clear_flag(lv.obj.FLAG.CLICKABLE) # self.circ_area.set_click(False)

        self.show_circle()

    def show_text(self, txt):
        self.label_main.set_text(txt)
        # self.label_main.set_align(lv.label.ALIGN.CENTER)
        self.label_main.set_pos((self.display.width() - self.label_main.get_width() ) // 2,
                                (self.display.height() - self.label_main.get_height()) // 2)
    def show_circle(self):
        point = self.points[self.cur_point]
        remaining = self.touch_count - self.cur_touch
        text = f'Click the circle in\n{point.name}\n({remaining} clicks remaining)'
        self.show_text(text)
        if point.display_coordinates.x < 0:
            point.display_coordinates.x += self.display.width()
        if point.display_coordinates.y < 0:
            point.display_coordinates.y += self.display.height()
        x = point.display_coordinates.x - Calibration_GUI.CIRCLE_SIZE // 2
        y = point.display_coordinates.y - Calibration_GUI.CIRCLE_SIZE // 2
        print(f'Show Circle coordinates: (x={x}, y={y})')
        self.circ_area.set_pos(x, y)

    def _calibrate_clicked(self, event):
        point = self.points[self.cur_point]
        indev = event.get_indev()
        indev.get_point(self.med[self.cur_touch])
        x = self.med[self.cur_touch].x
        y = self.med[self.cur_touch].y
        print(f'_calibrate_clicked(): (x={x}, y={y})')

        self.cur_touch += 1
        if self.cur_touch == self.touch_count:
            med_x = sorted([med.x for med in self.med])
            med_y = sorted([med.y for med in self.med])
            x = med_x[len(med_x) // 2]
            y = med_y[len(med_y) // 2]
            point.touch_coordinate = lv.point_t({'x': x, 'y': y})
            self.cur_point += 1
            self.cur_touch = 0

        if self.cur_point == len(self.points):
            cal = self._calibrate()
            self.show_text(f'Calibration result: x1={cal[0]}, y1={cal[1]}, x2={cal[2]}, y2={cal[3]}')
            self.cur_point = 0
            # self.show_text('Click/drag on screen\nto check calibration')
            # self.big_btn.add_event_cb(lambda event, self=self: self._check(event), lv.EVENT.PRESSING, None)
        else:
            self.show_circle()

    def _calibrate(self):
        dx1 = self.points[0].display_coordinates.x
        dy1 = self.points[0].display_coordinates.y
        dx2 = self.points[1].display_coordinates.x
        dy2 = self.points[1].display_coordinates.y
        print(f'Display coordinates: ({dx1}, {dy1}) ({dx2}, {dy2})')

        tx1 = self.points[0].touch_coordinate.x
        ty1 = self.points[0].touch_coordinate.y
        tx2 = self.points[1].touch_coordinate.x
        ty2 = self.points[1].touch_coordinate.y
        print(f'Touch coordinates: ({tx1}, {ty1}) ({tx2}, {ty2})')

        visual_width = self.points[1].display_coordinates.x - self.points[0].display_coordinates.x
        visual_height = self.points[1].display_coordinates.y - self.points[0].display_coordinates.y
        touch_width = self.points[1].touch_coordinate.x - self.points[0].touch_coordinate.x
        touch_height = self.points[1].touch_coordinate.y - self.points[0].touch_coordinate.y
        print(f'visual: (w={visual_width}, h={visual_height}), touch (w={touch_width}, h={touch_height})')

        pixel_width = touch_width / visual_width
        pixel_height = touch_height / visual_height
        print(f'Pixel: (w={pixel_width}, h={pixel_height})')

        x1 = tx1 - dx1 * pixel_width
        y1 = ty1 - dy1 * pixel_height
        x2 = tx2 + (self.display.width() - dx2) * pixel_width
        y2 = ty2 + (self.display.height() - dy2) * pixel_height
        print(f'Calibration result: x1={round(x1)}, y1={round(y1)}, x2={round(x2)}, y2={round(y2)}')
        return (x1, y1, x2, y2)

    # def _check(self, event):
    #     point = lv.point_t()
    #     indev = event.get_indev()
    #     indev.get_point(point)
    #     print(f'click position: (x={point.x}, y={point.y})')
    #     self.circ_area.set_pos(point.x - Calibration_GUI.CIRCLE_SIZE // 2,
    #                            point.y - Calibration_GUI.CIRCLE_SIZE // 2)