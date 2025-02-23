import os

script_dir = os.path.dirname(os.path.abspath(__file__))
save_folder = os.path.join(script_dir, "logs")

def setup_log():
    os.makedirs(save_folder, exist_ok=True)
