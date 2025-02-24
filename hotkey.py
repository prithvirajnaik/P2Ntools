import keyboard
from editor_screen import toggle_monitor
from home_screen import create_new_file
from utils import exit_program

def set_hotkey():
    keyboard.add_hotkey("shift+alt+c", toggle_monitor)
    keyboard.add_hotkey("shift+alt+n", create_new_file)
    keyboard.add_hotkey("shift+alt+q", exit_program)