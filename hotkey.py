import keyboard
from editor_frame import toggle_monitor
from home_screen import create_new_file


def set_hotkey():
    keyboard.add_hotkey("shift+alt+c", toggle_monitor)
    keyboard.add_hotkey("shift+alt+n", create_new_file)