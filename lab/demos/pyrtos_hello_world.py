import pyRTOS as rtos
import lvgl as lv

from lab import display_tools
from lab.pyrtos_tools import display_event_loop
from lab.demos.lvgl_hello_world import lv_hello_world, lv_anim_arc

def main():
    # Init display driver
    d = display_tools.get_display()

    # Init pyRTOS display task
    t_display = rtos.Task(display_event_loop, priority=0, name="display", notifications=None, mailbox=False)
    rtos.add_task(t_display)

    # Init demo
    # (This could be done in a separate Task instead.)
    if not lv.is_initialized():
        lv.init()
    lv_hello_world()
    lv_anim_arc()

    # Hand control over to the OS. This is a blocking call, there can't be other statements after that.
    rtos.start()


if __name__ == '__main__':
    main()