import lvgl as lv

from lab import gyro_tools
from lab import display_tools

def main():
    gyro = gyro_tools.get_gyro()
    gm = gyro_tools.GyroMadgwick()

    d = display_tools.get_display()
    w, h = d.width(), d.height()

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

    for pitch, roll in gm.run(gyro):
        bar1.set_value(int(pitch), lv.ANIM.OFF)
        bar2.set_value(int(roll), lv.ANIM.OFF)


if __name__ == '__main__':
    main()