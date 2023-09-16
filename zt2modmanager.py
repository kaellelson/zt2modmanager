import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox

zoo_tycoon_folder = "C:\\Path\\To\\ZooTycoon2"
mod_folder = "C:\\Path\\To\\ModFolder"

mod_data = {
    "Mod1.z2f": {
        "description": "This is the description for Mod 1.",
        "version": "1.0",
        "dependencies": [],
    },
    "Mod2.z2f": {
        "description": "This is the description for Mod 2.",
        "version": "2.0",
        "dependencies": ["Mod1.z2f"],
    },
}

mods_per_page = 50

current_page = 1

mod_descriptions = {
    "mod1.z2f": "This is the description for Mod 1.",
    "mod2.z2f": "This is the description for Mod 2.",
}

def list_mods():
    """List all installed mods with descriptions in the GUI."""
    mod_listbox.delete(0, tk.END)
    mods = os.listdir(mod_folder)
    for mod in mods:
        description = mod_descriptions.get(mod, "No description available.")
        mod_listbox.insert(tk.END, f"{mod} - {description}")

def next_page():
    """Go to the next page of mods."""
    global current_page
    current_page += 1
    list_mods()

def prev_page():
    """Go to the previous page of mods."""
    global current_page
    if current_page > 1:
        current_page -= 1
        list_mods()

def install_mod():
    """Install a mod by copying it to the selected mod folder."""
    mod_path = filedialog.askopenfilename(title="Select a mod file")
    if mod_path:
        if os.path.isfile(mod_path):
            selected_folder = folder_listbox.get(folder_listbox.curselection())
            if selected_folder:
                folder_path = os.path.join(mod_folder, selected_folder)
                mod_name = os.path.basename(mod_path)
                destination = os.path.join(folder_path, mod_name)
                shutil.copy(mod_path, destination)
                list_mods()
                status_label.config(text=f"Installed: {mod_name}")
            else:
                status_label.config(text="No mod folder selected.")
        else:
            status_label.config(text="Invalid mod file path.")

def uninstall_mod():
    """Uninstall a mod by removing it from the mod folder."""
    selected_mod = mod_listbox.get(mod_listbox.curselection())
    if selected_mod:
        mod_name = selected_mod.split(" - ")[0]
        mod_path = os.path.join(mod_folder, mod_name)
        if os.path.exists(mod_path):
            os.remove(mod_path)
            list_mods()
            status_label.config(text=f"Uninstalled: {mod_name}")
        else:
            status_label.config(text="Mod not found.")

def create_mod_folder():
    """Create a new mod folder."""
    new_folder_name = simpledialog.askstring("Create Folder", "Enter a name for the new mod folder:")
    if new_folder_name:
        new_folder_path = os.path.join(mod_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        folder_listbox.insert(tk.END, new_folder_name)

def delete_mod_folder():
    """Delete the selected mod folder."""
    selected_folder = folder_listbox.get(folder_listbox.curselection())
    if selected_folder:
        response = messagebox.askyesno("Delete Folder", f"Are you sure you want to delete the folder '{selected_folder}'?")
        if response:
            folder_path = os.path.join(mod_folder, selected_folder)
            shutil.rmtree(folder_path)
            folder_listbox.delete(folder_listbox.curselection())
            list_mods()

app = tk.Tk()
app.title("Zoo Tycoon 2 Mod Manager")

mod_listbox = tk.Listbox(app, width=50, height=10)
folder_listbox = tk.Listbox(app, width=30, height=10)
install_button = tk.Button(app, text="Install Mod", command=install_mod)
uninstall_button = tk.Button(app, text="Uninstall Mod", command=uninstall_mod)
refresh_button = tk.Button(app, text="Refresh List", command=list_mods)
create_folder_button = tk.Button(app, text="Create Mod Folder", command=create_mod_folder)
delete_folder_button = tk.Button(app, text="Delete Mod Folder", command=delete_mod_folder)
status_label = tk.Label(app, text="", fg="green")

folder_listbox.pack(side=tk.LEFT, padx=10, pady=10)
mod_listbox.pack(side=tk.RIGHT, padx=10, pady=10)
install_button.pack()
uninstall_button.pack()
refresh_button.pack()
create_folder_button.pack()
delete_folder_button.pack()
status_label.pack(pady=5)

list_mods()

app.mainloop()
