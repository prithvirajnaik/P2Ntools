from setup_config import *
from frames import *
from home_screen import *
from hotkey import set_hotkey

setup_log()
set_hotkey()
load_file_list()


# Run App
app.mainloop()
