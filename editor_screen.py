import pyperclip
import os
import time
import threading
from tkinter import messagebox
from clip_notifications import show_copied_notification,show_toggle_notification
from utils import *
from home_screen import load_file_list
from frames import *
import setting

def monitor_clipboard():

    while setting.running and setting.current_file:
        clipboard_content = pyperclip.paste() or ""  # Ensure it's always a string

        if setting.monitoring_started and clipboard_content and clipboard_content != setting.last_clipboard:
            setting.last_clipboard = clipboard_content

            # Check if the file still exists before writing
            if not os.path.exists(setting.current_file):
                setting.running = False
                setting.monitoring_started = False
                app.after(0, lambda: messagebox.showerror("Error", "Selected file was deleted. Monitoring stopped."))
                return

            existing_content = editor.get("1.0", tk.END).strip()  # Read editor content
            
            # Open file in write mode and save both manual edits & clipboard data
            with open(setting.current_file, "w", encoding="utf-8") as f:
                f.write(existing_content + "\n" + clipboard_content + "\n")

            show_copied_notification(clipboard_content)

            # Update the text editor with new content
            app.after(100, update_editor)

        time.sleep(1)  # Delay to prevent high CPU usage


def update_editor():
    if setting.current_file and os.path.exists(setting.current_file):
        with open(setting.current_file, "r", encoding="utf-8") as f:
            editor.delete("1.0", tk.END)
            editor.insert("1.0", f.read())
    else:
        editor.delete("1.0", tk.END)  # Clear editor if file doesn't exist



def toggle_monitor():


    if not setting.current_file:
        messagebox.showwarning("No File Selected", "Please open a file before starting monitoring.")
        return

    # Auto-save before monitoring
    with open(setting.current_file, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END).strip())

    if setting.running:
        setting.running = False
        setting.monitoring_started = False
        start_button.configure(text="Start Monitoring", fg_color="green")
        show_toggle_notification("monitoring stopped")
    else:
        if not setting.monitoring_started:  # Only start a new thread if it's not already running
            setting.running = True
            setting.monitoring_started = True
            pyperclip.copy("")  # Clear clipboard
            start_button.configure(text="Stop Monitoring", fg_color="red")
            show_toggle_notification("monitoring started")
            
            monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
            monitor_thread.start()

# Save the edited file
def save_file():
    if not setting.current_file:
        # messagebox.showwarning("No File Selected", "Please open a file first.")
        show_custom_message(app,"No File Selected", "Please open a file first.", "#ff9900")    
        return
    
    with open(setting.current_file, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END).strip())

    show_custom_message(app,"File Saved", "Changes have been saved.", "#44bb44")

# Go back to home screen
def go_back(): 
    setting.current_file = None
    if setting.running:
        setting.running = False
        setting.monitoring_started = False
        start_button.configure(text="Start Monitoring", fg_color="green")
    editor_frame.pack_forget()
    nav_frame.pack(fill="x", side="top")
    home_frame.pack(fill="both", expand=True)
    load_file_list()


save_button = ctk.CTkButton(editor_header, text="💾 Save", width=80, command=save_file)
save_button.pack(side="right", padx=5)

start_button = ctk.CTkButton(editor_header, text="▶ Start", width=100, command=toggle_monitor, fg_color="green")
start_button.pack(side="right", padx=5)

back_button = ctk.CTkButton(editor_header, text="⬅ Back", width=80, command=go_back)
back_button.pack(side="right", padx=5)