import sys

import pyRTOS
import lvgl as lv


DISPLAY_FREQ = 25


# self is the thread object this runs in
def display_event_loop(self):
    ### Setup code here
    if not lv.is_initialized():
        lv.init()
    # ns <-- us <-- ms <-- s
    delay_ns = 1000 * 1000 * 1000 * 1.0 / DISPLAY_FREQ
    ### End Setup code

    # Pass control back to RTOS
    yield

    # Thread loop
    while True:
        ### Work code here
        # If there is significant code here, yield periodically
        # between instructions that are not timing dependent.
        # Also, it is generally a good idea to yield after
        # I/O commands that return instantly but will require
        # some time to complete (like I2C data requests).
        # Each task must yield at least one per iteration,
        # or it will hog all of the CPU, preventing any other
        # task from running.
        try:
            lv.task_handler()
        except Exception as e:
            sys.print_exception(e)
        ### End Work code

        yield [pyRTOS.timeout_ns(delay_ns)]


def main():
    t_display = pyRTOS.Task(display_event_loop, priority=0, name="display", notifications=None, mailbox=False)
    pyRTOS.add_task(t_display)
    pyRTOS.start()


if __name__ == '__main__':
    main()