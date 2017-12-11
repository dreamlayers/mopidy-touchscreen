# flake8: noqa
from input_manager import InputManager
from input_manager import InputEvent
try:
    from lirc_input_manager import LIRCManager
    from gpio_inpput_manager import GPIOManager
except ImportError:
    pass
