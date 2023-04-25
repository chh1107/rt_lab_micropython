import lvgl as lv

from lab import display_tools


# LVGL code from https://docs.lvgl.io/master/examples.html#get-started
def lv_hello_world():
    # Change the active screen's background color
    scr = lv.scr_act()
    scr.set_style_bg_color(lv.color_hex(0x003a57), lv.PART.MAIN)

    # Create a white label, set its text and align it to the center
    label = lv.label(lv.scr_act())
    label.set_text("Hello world")
    label.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
    label.align(lv.ALIGN.CENTER, 0, 0)

def lv_anim_arc():
    # Create an arc
    arc = lv.arc(lv.scr_act())
    arc.set_bg_angles(0, 360)
    arc.set_angles(270, 270)
    arc.center()

    # Helper class, called periodically to set the angles of the arc
    class ArcLoader():
        def __init__(self):
            self.a = 270

        def arc_loader_cb(self, tim, arc):
            self.a += 5
            arc.set_end_angle(self.a)
            if self.a >= 270 + 360:
                tim._del()

    # Create the animation to update the arc
    arc_loader = ArcLoader()
    timer = lv.timer_create_basic()
    timer.set_period(20)
    timer.set_cb(lambda src: arc_loader.arc_loader_cb(timer, arc))


def main():
    d = display_tools.get_display()

    import lv_utils
    if not lv_utils.event_loop.is_running():
        lv_utils.event_loop()

    lv_hello_world()
    lv_anim_arc()


if __name__ == '__main__':
    main()