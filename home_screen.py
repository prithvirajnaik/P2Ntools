import os

from frames import *
from setup_config import save_folder
import setting 
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

        delete_button = ctk.CTkButton(header_frame, text="❌", width=30, height=30,hover_color="red",
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


def delete_file(filename):
    file_path = os.path.join(save_folder, filename)
    os.remove(file_path)
    load_file_list()

# Open a selected file
def open_file(filename):
    setting.current_file
    setting.current_file = os.path.join(save_folder, filename)

    with open(setting.current_file, "r", encoding="utf-8") as f:
        editor.delete("1.0", tk.END)
        editor.insert("1.0", f.read())

    log_label.configure(text=f"Editing: {filename}")
    switch_to_editor()

# Switch to file editor view
def switch_to_editor():
    nav_frame.pack_forget()
    home_frame.pack_forget()
    editor_frame.pack(fill="both", expand=True)

# Create a new file
def create_new_file():
    app.after(0, _create_new_file) #to make below fucntion run on the main thread

def _create_new_file():
    # global current_file
    # filename = simpledialog.askstring("New File", "Enter file name (without extension):")
    dialog = ctk.CTkInputDialog(text="Enter file name (without extension):", title="Create New File")
    filename = dialog.get_input()
    if not filename:
        return
    
    new_file_path = os.path.join(save_folder, f"{filename}.txt")
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write("")

    load_file_list()


new_button = ctk.CTkButton(nav_frame, text="➕",fg_color="transparent", command=create_new_file,width=50)
new_button.pack(side="right", padx=15 , pady=5)