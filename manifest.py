# from lv_micropython/ports/stm32/boards/manifest.py
include("$(MPY_DIR)/extmod/uasyncio/manifest.py")
freeze("$(MPY_DIR)/drivers/onewire", "onewire.py")

# from TH
freeze("$(MPY_DIR)/lib/lv_bindings/lib", "lv_utils.py")

freeze(".",
    (
        "lab/__init__.py",
        "lab/colors.py",
        "lab/deltat.py",
        "lab/device_tools.py",
        "lab/display_tools.py",
        "lab/gyro_tools.py",
        "lab/demos/__init__.py",
        "lab/demos/lvgl_hello_world.py",
    ),
)