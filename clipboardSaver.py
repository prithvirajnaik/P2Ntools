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
prev_width = 0  
prev_columns = 0  
resize_job = None  # Store reference to pending resize job

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


# def monitor_clipboard():
#     global running, last_clipboard, monitoring_started, current_file
#     while running and current_file:
#         clipboard_content = pyperclip.paste()

#         if clipboard_content is None:  # Fix: Handle NoneType
#             clipboard_content = ""
                   


#         if monitoring_started and clipboard_content and clipboard_content != last_clipboard:
#             last_clipboard = clipboard_content
#             with open(current_file, "w", encoding="utf-8") as f: #save any manually made changes to text while monitoring was on
#                 f.write(editor.get("1.0", tk.END).strip())
#             with open(current_file, "a", encoding="utf-8") as f:
#                 f.write(clipboard_content + "\n")

#             show_notification(clipboard_content)

#             # Update the text editor with new content
#             app.after(100, update_editor)

#         time.sleep(1)

def monitor_clipboard():
    global running, last_clipboard, monitoring_started, current_file

    while running and current_file:
        clipboard_content = pyperclip.paste() or ""  # Ensure it's always a string

        if monitoring_started and clipboard_content and clipboard_content != last_clipboard:
            last_clipboard = clipboard_content

            # Check if the file still exists before writing
            if not os.path.exists(current_file):
                running = False
                monitoring_started = False
                app.after(0, lambda: messagebox.showerror("Error", "Selected file was deleted. Monitoring stopped."))
                return

            existing_content = editor.get("1.0", tk.END).strip()  # Read editor content
            
            # Open file in write mode and save both manual edits & clipboard data
            with open(current_file, "w", encoding="utf-8") as f:
                f.write(existing_content + "\n" + clipboard_content + "\n")

            show_notification(clipboard_content)

            # Update the text editor with new content
            app.after(100, update_editor)

        time.sleep(1)  # Delay to prevent high CPU usage


def update_editor():
    if current_file and os.path.exists(current_file):
        with open(current_file, "r", encoding="utf-8") as f:
            editor.delete("1.0", tk.END)
            editor.insert("1.0", f.read())
    else:
        editor.delete("1.0", tk.END)  # Clear editor if file doesn't exist



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
        monitoring_started = False
        start_button.configure(text="Start Monitoring", fg_color="green")
    else:
        if not monitoring_started:  # Only start a new thread if it's not already running
            running = True
            monitoring_started = True
            pyperclip.copy("")  # Clear clipboard
            start_button.configure(text="Stop Monitoring", fg_color="red")
            
            monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
            monitor_thread.start()


 
def load_file_list():
    # Clear existing widgets
    for widget in file_list_frame.winfo_children():
        widget.destroy()

    files = [f for f in os.listdir(save_folder) if f.endswith(".txt")]

    if not files:
        no_files_label = ctk.CTkLabel(file_list_frame, text="No saved files yet.", font=("Arial", 16))
        no_files_label.pack(pady=10)
        return

    # 🛠 **Dynamic Card Width Settings**
    window_width = app.winfo_width()
    min_width = 200   # Minimum width of the card
    max_width = 300   # Maximum width of the card
    calculated_width = max(min_width, min(max_width, window_width // 3))  # Dynamic width

    num_columns = 2 if window_width < 700 else 3# Adjust column count

    for index, file in enumerate(files):
        row, col = divmod(index, num_columns)

        file_path = os.path.join(save_folder, file)

        # Read file preview (first 3 lines)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                preview_content = "\n".join(f.readlines()[:3])
        except:
            preview_content = "Error loading file."

        # 🔹 **Create a card with dynamic width**
        card = ctk.CTkFrame(file_list_frame, fg_color="#212121", corner_radius=10)
        card.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")

        # 🔹 **Header Frame (File Name + Delete Button)**
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)

        file_label = ctk.CTkLabel(header_frame, text=file, font=("Arial", 14, "bold"), anchor="w")
        file_label.pack(side="left", padx=5)

        delete_button = ctk.CTkButton(header_frame, text="❌", width=30, height=30,
                                      fg_color="transparent",command=lambda f=file: delete_file(f))
        delete_button.pack(side="right", padx=5)

        # **Preview Text**
        preview_label = ctk.CTkLabel(card, text=preview_content, font=("Arial", 12), wraplength=calculated_width - 20, justify="left")
        preview_label.pack(side = "left" , pady=5, padx=15)


        # Open file when clicking the card
        card.bind("<Button-1>", lambda event, f=file: open_file(f))
        file_label.bind("<Button-1>", lambda event, f=file: open_file(f))
        preview_label.bind("<Button-1>", lambda event, f=file: open_file(f))

    # Make the grid responsive
    for i in range(num_columns):
        file_list_frame.columnconfigure(i, weight=1)





def on_resize(event):
    global prev_width, prev_columns, resize_job

    current_width = app.winfo_width()

    # Determine the number of columns based on window width
    num_columns = 2 if current_width < 700 else 3  

    # Only reload if:
    # - The number of columns actually changes
    # - The width has changed significantly (150px or more)
    if  num_columns == prev_columns:
        return  # Skip unnecessary reloads

    # Update previous values
    prev_width = current_width
    prev_columns = num_columns  

    # Cancel any pending reload
    if resize_job:
        app.after_cancel(resize_job)

    # Delay reload to prevent excessive calls while resizing
    resize_job = app.after(0, load_file_list)  # Debounce delay increased to 500ms



def delete_file(filename):
    file_path = os.path.join(save_folder, filename)
    os.remove(file_path)
    load_file_list()

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
    app.after(0, _create_new_file) #to make below fucntion run on the main thread

def _create_new_file():
    global current_file
    filename = simpledialog.askstring("New File", "Enter file name (without extension):")
    if not filename:
        return
    
    new_file_path = os.path.join(save_folder, f"{filename}.txt")
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write("")

    load_file_list()


# Switch to file editor view
def switch_to_editor():
    nav_frame.pack_forget()
    home_frame.pack_forget()
    editor_frame.pack(fill="both", expand=True)

# Go back to home screen
def go_back():
    global running , monitoring_started ,current_file
    current_file = None
    if running:
        running = False
        monitoring_started = False
        start_button.configure(text="Start Monitoring", fg_color="green")
    editor_frame.pack_forget()
    nav_frame.pack(fill="x", side="top")
    home_frame.pack(fill="both", expand=True)
    load_file_list()

# Register global hotkey
keyboard.add_hotkey("shift+alt+c", toggle_monitor)
keyboard.add_hotkey("shift+alt+n", create_new_file)


# GUI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
# Bind window resize event
app.bind("<Configure>", on_resize)

app.title("Clipboard Saver")
app.geometry("700x500")
app.minsize(500, 500)  # Set minimum width to 500px and height to 500px

# --- Navigation Bar ---
nav_frame = ctk.CTkFrame(app, fg_color="#333333", height=50,corner_radius=0)
nav_frame.pack(fill="x", side="top")


# --- Home Screen ---
home_frame = ctk.CTkFrame(app,corner_radius=0)
home_frame.pack(fill="both", expand=True)


title_label = ctk.CTkLabel(nav_frame, text="📋 Clipboard Saver", font=("Arial", 18, "bold"))
title_label.pack(side="left", padx=15, pady=5)



file_list_frame = ctk.CTkFrame(home_frame)
file_list_frame.pack(fill="both", expand=True, padx=25, pady=25)


new_button = ctk.CTkButton(nav_frame, text="➕",fg_color="transparent", command=create_new_file,width=50)
new_button.pack(side="right", padx=15 , pady=5)


editor_frame = ctk.CTkFrame(app)

# Header frame for file name + buttons
editor_header = ctk.CTkFrame(editor_frame, fg_color="transparent")
editor_header.pack(fill="x", padx=10, pady=15, anchor="w")

log_label = ctk.CTkLabel(editor_header, text="No file selected", font=("Arial", 14))
log_label.pack(side="left", padx=5)

# Buttons aligned to the right of the file name
save_button = ctk.CTkButton(editor_header, text="💾 Save", width=80, command=save_file)
save_button.pack(side="right", padx=5)

start_button = ctk.CTkButton(editor_header, text="▶ Start", width=100, command=toggle_monitor, fg_color="green")
start_button.pack(side="right", padx=5)

back_button = ctk.CTkButton(editor_header, text="⬅ Back", width=80, command=go_back)
back_button.pack(side="right", padx=5)

# Text Editor
editor = tk.Text(editor_frame, wrap="word", height=14,font=("Arial", 18))
editor.pack(padx=20, pady=20, fill="both", expand=True)

# Add inner padding
# editor.tag_configure("margin", lmargin1=20, lmargin2=20, rmargin=20)
# editor.insert("1.0", "", "margin")  # Apply margin to all text
# Load files on startup
load_file_list()


# Run App
app.mainloop()
