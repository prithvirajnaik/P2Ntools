import customtkinter as ctk 
from frames import *
import setting
from home_screen import load_file_list

def show_custom_message(app, title, message, color="#ff4444"):
    popup = ctk.CTkToplevel(app)
    popup.title(title)
    popup.geometry("400x200")
    popup.resizable(False, False)
    
    popup_label = ctk.CTkLabel(popup, text=message, font=("Arial", 14), wraplength=350)
    popup_label.pack(pady=20, padx=20)
    
    ok_button = ctk.CTkButton(popup, text="OK", fg_color=color, command=popup.destroy)
    ok_button.pack(pady=10)

    popup.grab_set()  # Makes the dialog modal
    popup.mainloop()

def on_resize(event):
    current_width = app.winfo_width()
    # print(current_width)
    # Determine the number of columns based on window width
    num_columns = 2 if current_width < 1000 else 3  
    # print(num_columns)
    # Only reload if:
    # - The number of columns actually changes
    # - The width has changed significantly (150px or more)
    if  num_columns == setting.prev_columns:
        return  # Skip unnecessary reloads

    # Update previous values
    setting.prev_width = current_width
    setting.prev_columns = num_columns  

    # Cancel any pending reload
    if setting.resize_job:
        app.after_cancel(setting.resize_job)

    # Delay reload to prevent excessive calls while resizing
    setting.resize_job = app.after(0, load_file_list)  # Debounce delay increased to 500ms

app.bind("<Configure>", on_resize)

def exit_program():
    print("Exiting program")
    app.quit()