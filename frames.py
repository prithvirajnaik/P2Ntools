import customtkinter as ctk
import tkinter as tk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


app = ctk.CTk()
app.title("Clipboard Saver")
app.geometry("700x500")
app.minsize(500, 500)

nav_frame = ctk.CTkFrame(app, fg_color="#333333", height=50,corner_radius=0)
nav_frame.pack(fill="x", side="top")

home_frame = ctk.CTkFrame(app,corner_radius=0)
home_frame.pack(fill="both", expand=True)

title_label = ctk.CTkLabel(nav_frame, text="📋 Clipboard Saver", font=("Arial", 18, "bold"))
title_label.pack(side="left", padx=15, pady=5)

file_list_frame = ctk.CTkFrame(home_frame)
file_list_frame.pack(fill="both", expand=True, padx=25, pady=25)

editor_frame = ctk.CTkFrame(app)

# Header frame for file name + buttons
editor_header = ctk.CTkFrame(editor_frame, fg_color="transparent")
editor_header.pack(fill="x", padx=10, pady=15, anchor="w")

log_label = ctk.CTkLabel(editor_header, text="No file selected", font=("Arial", 14))
log_label.pack(side="left", padx=5)


editor = tk.Text(editor_frame, wrap="word", height=14,font=("Arial", 18))
editor.pack(padx=20, pady=20, fill="both", expand=True)
