import customtkinter as ctk
import pyperclip
import threading
import os
import time
import keyboard
from plyer import notification
import tkinter as tk
from tkinter import simpledialog, messagebox

# Global Variables
running = False
last_clipboard = ""
monitoring_started = False
current_file = None

# Setup logs folder
script_dir = os.path.dirname(os.path.abspath(__file__))
save_folder = os.path.join(script_dir, "logs")
os.makedirs(save_folder, exist_ok=True)

# Show Windows notification
def show_notification(text):
    notification.notify(
        title="Clipboard Saved!",
        message=f"Copied: {text[:50]}...",  # Show first 50 characters
        timeout=2
    )

# Clipboard monitoring function
def monitor_clipboard():
    global running, last_clipboard, monitoring_started, current_file
    while running and current_file:
        clipboard_content = pyperclip.paste()
        
        if monitoring_started and clipboard_content and clipboard_content != last_clipboard:
            last_clipboard = clipboard_content
            with open(current_file, "a", encoding="utf-8") as f:
                f.write(clipboard_content + "\n")
            
            show_notification(clipboard_content)

            # Update the text editor with new content
            app.after(100, update_editor)

        time.sleep(1)

# Function to update editor with latest file content
def update_editor():
    if current_file:
        with open(current_file, "r", encoding="utf-8") as f:
            editor.delete("1.0", tk.END)
            editor.insert("1.0", f.read())



def toggle_monitor():
    global running, monitoring_started
    
    if not current_file:
        messagebox.showwarning("No File Selected", "Please open a file before starting monitoring.")
        return

    # Auto-save before monitoring
    with open(current_file, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END).strip())

    if running:
        running = False
        start_button.configure(text="Start Monitoring", fg_color="green")
    else:
        running = True
        monitoring_started = True
        pyperclip.copy("")  # Clear clipboard
        start_button.configure(text="Stop Monitoring", fg_color="red")
        
        threading.Thread(target=monitor_clipboard, daemon=True).start()


# Load available log files
def load_file_list():
    for widget in file_list_frame.winfo_children():
        widget.destroy()

    files = [f for f in os.listdir(save_folder) if f.endswith(".txt")]
    
    for file in files:
        file_button = ctk.CTkButton(
            file_list_frame, text=file, 
            command=lambda f=file: open_file(f),
            fg_color="#333333", hover_color="#555555",
            corner_radius=10, width=200, height=40
        )
        file_button.pack(pady=5, padx=10, fill="x")

# Open a selected file
def open_file(filename):
    global current_file
    current_file = os.path.join(save_folder, filename)

    with open(current_file, "r", encoding="utf-8") as f:
        editor.delete("1.0", tk.END)
        editor.insert("1.0", f.read())

    log_label.configure(text=f"Editing: {filename}")
    switch_to_editor()

# Save the edited file
def save_file():
    if not current_file:
        messagebox.showwarning("No File Selected", "Please open a file first.")
        return
    
    with open(current_file, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END).strip())

    messagebox.showinfo("File Saved", "Changes have been saved.")

# Create a new file
def create_new_file():
    global current_file
    filename = simpledialog.askstring("New File", "Enter file name (without extension):")
    if not filename:
        return
    
    new_file_path = os.path.join(save_folder, f"{filename}.txt")
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write("")

    load_file_list()

# Delete a selected file
def delete_file():
    selected_files = os.listdir(save_folder)
    if not selected_files:
        messagebox.showwarning("No Files", "There are no files to delete.")
        return
    
    filename = simpledialog.askstring("Delete File", "Enter file name to delete (without extension):")
    if not filename:
        return

    file_path = os.path.join(save_folder, f"{filename}.txt")

    if os.path.exists(file_path):
        os.remove(file_path)
        load_file_list()
        messagebox.showinfo("File Deleted", f"'{filename}.txt' has been deleted.")
    else:
        messagebox.showerror("Error", "File not found.")

# Switch to file editor view
def switch_to_editor():
    home_frame.pack_forget()
    editor_frame.pack(fill="both", expand=True)

# Go back to home screen
def go_back():
    global current_file
    current_file = None
    editor_frame.pack_forget()
    home_frame.pack(fill="both", expand=True)
    load_file_list()

# Register global hotkey
keyboard.add_hotkey("shift+alt+c", toggle_monitor)

# GUI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Clipboard Saver")
app.geometry("600x500")

# --- Home Screen ---
home_frame = ctk.CTkFrame(app)
home_frame.pack(fill="both", expand=True)

title_label = ctk.CTkLabel(home_frame, text="Clipboard Saver", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

file_list_frame = ctk.CTkFrame(home_frame)
file_list_frame.pack(fill="both", expand=True, padx=25, pady=5)

button_frame = ctk.CTkFrame(home_frame)
button_frame.pack(pady=5)

new_button = ctk.CTkButton(button_frame, text="New File", command=create_new_file)
new_button.grid(row=0, column=0, padx=5)

delete_button = ctk.CTkButton(button_frame, text="Delete File", command=delete_file)
delete_button.grid(row=0, column=1, padx=5)

# --- Editor Screen ---
editor_frame = ctk.CTkFrame(app)

log_label = ctk.CTkLabel(editor_frame, text="No file selected", font=("Arial", 14))
log_label.pack(pady=5)

editor = tk.Text(editor_frame, wrap="word", height=14,font=("Arial", 18))
editor.pack(padx=10, pady=5, fill="both", expand=True)

save_button = ctk.CTkButton(editor_frame, text="Save File", command=save_file)
save_button.pack(pady=5)

start_button = ctk.CTkButton(editor_frame, text="Start Monitoring", command=toggle_monitor, fg_color="green")
start_button.pack(pady=5)

back_button = ctk.CTkButton(editor_frame, text="Go Back", command=go_back)
back_button.pack(pady=5)  

# Load files on startup
load_file_list()

# Run App
app.mainloop()
