import os
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import threading
import json

zoo_tycoon_folder = "C:\\Path\\To\\ZooTycoon2"
mod_folder = "C:\\Path\\To\\ModFolder"


mod_data = {
    # ...
}

mods_per_page = 50

current_page = 1

current_category = "All"

current_folder = "All"

update_check_interval = 3600

backup_folder = "C:\\Path\\To\\BackupFolder"

def create_profile():
    new_profile = simpledialog.askstring("Create Profile", "Enter a name for the new profile:")
    if new_profile:
        profiles[new_profile] = []
        profile_combobox["values"] = list(profiles.keys())
        profile_combobox.set(new_profile)
        activate_profile(new_profile)

def delete_profile():
    selected_profile = profile_combobox.get()
    if selected_profile != "Default":
        response = messagebox.askyesno("Delete Profile", f"Delete the profile '{selected_profile}' and its mods?")
        if response:
            del profiles[selected_profile]
            profile_combobox["values"] = list(profiles.keys())
            profile_combobox.set("Default")
            activate_profile("Default")
            list_mods()

def activate_profile(profile_name):
    global current_profile
    current_profile = profile_name
    list_mods()

def list_mods():
    """List installed mods with descriptions, versions, and dependencies on the current page."""
    start_index = (current_page - 1) * mods_per_page
    end_index = start_index + mods_per_page
    mod_listbox.delete(0, tk.END)
    mods_to_display = list(mod_data.keys())[start_index:end_index]

    for mod_name in mods_to_display:
        mod_info = mod_data[mod_name]
        if (current_category == "All" or mod_info["category"] == current_category) and \
           (current_folder == "All" or mod_info["folder"] == current_folder):
            description = mod_info["description"]
            version = mod_info["version"]
            dependencies = ", ".join(mod_info["dependencies"])
            num_ratings = len(mod_info["ratings"])
            mod_listbox.insert(tk.END, f"{mod_name} - {description} (v{version}) - Dependencies: {dependencies} - Ratings: {num_ratings}")

def sort_mods():
    """Sort the displayed mods based on selected sorting criteria."""
    sort_criteria = sort_combobox.get()
    reverse_sort = sort_reverse_var.get()

    mods_to_sort = [(mod_name, mod_data[mod_name]) for mod_name in mod_data.keys()]
    mods_to_sort.sort(key=lambda x: x[1][sort_criteria], reverse=reverse_sort)

    mod_listbox.delete(0, tk.END)
    for mod_name, mod_info in mods_to_sort:
        description = mod_info["description"]
        version = mod_info["version"]
        dependencies = ", ".join(mod_info["dependencies"])
        num_ratings = len(mod_info["ratings"])
        mod_listbox.insert(tk.END, f"{mod_name} - {description} (v{version}) - Dependencies: {dependencies} - Ratings: {num_ratings}")

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

def filter_category(event):
    """Filter mods by category."""
    global current_category
    current_category = category_combobox.get()
    current_page = 1
    list_mods()

def filter_folder(event):
    """Filter mods by folder."""
    global current_folder
    current_folder = folder_combobox.get()
    current_page = 1
    list_mods()

def install_mod():
    """Install a mod by copying it to the selected mod folder."""
    mod_path = filedialog.askopenfilename(title="Select a mod file")
    if mod_path:
        if os.path.isfile(mod_path):
            selected_folder = folder_combobox.get()
            if selected_folder:
                folder_path = os.path.join(mod_folder, selected_folder)
                mod_name = os.path.basename(mod_path)
                destination = os.path.join(folder_path, mod_name)

                if os.path.exists(destination):
                    response = messagebox.askyesno("Overwrite Mod", f"The mod '{mod_name}' already exists. Overwrite?")
                    if not response:
                        return

                shutil.copy(mod_path, destination)
                list_mods()
                status_label.config(text=f"Installed: {mod_name}")
            else:
                status_label.config(text="No mod folder selected.")
        else:
            status_label.config(text="Invalid mod file path.")

def check_for_updates():
    """Check for updates of installed mods in the background."""
    for mod_name, mod_info in mod_data.items():
        update_url = mod_info.get("update_url")
        if update_url:
            try:
                response = requests.get(update_url)
                if response.status_code == 200:
                    update_info = response.json()
                    new_version = update_info.get("version")
                    if new_version and new_version != mod_info["version"]:
                        messagebox.showinfo(
                            "Update Available",
                            f"A new update for {mod_name} is available (v{new_version})."
                        )
            except Exception as e:
                print(f"Error checking for updates for {mod_name}: {e}")

def detect_conflicts():
    """Detect conflicts between installed mods based on their dependencies."""
    conflicts = {}
    for mod_name, mod_info in mod_data.items():
        for dependency in mod_info["dependencies"]:
            if dependency in conflicts:
                conflicts[dependency].append(mod_name)
            else:
                conflicts[dependency] = [mod_name]

    if conflicts:
        conflict_message = "Conflicts detected:\n"
        for dependency, conflicting_mods in conflicts.items():
            conflict_message += f"- {dependency} is required by: {', '.join(conflicting_mods)}\n"
        messagebox.showerror("Conflicts Detected", conflict_message)
    else:
        messagebox.showinfo("No Conflicts", "No conflicts detected.")

def backup_mods():
    """Create a backup of installed mods and their configurations."""
    backup_path = filedialog.askdirectory(title="Select a backup folder")
    if backup_path:
        backup_info = {
            "mods": mod_data,
            "current_page": current_page,
            "current_category": current_category,
            "current_folder": current_folder,
        }
        backup_file = os.path.join(backup_path, "mod_manager_backup.json")
        with open(backup_file, "w") as f:
            json.dump(backup_info, f)
        messagebox.showinfo("Backup Complete", "Mod manager backup created successfully.")

def restore_mods():
    """Restore mods and their configurations from a backup."""
    backup_file = filedialog.askopenfilename(title="Select a mod manager backup file", filetypes=[("JSON Files", "*.json")])
    if backup_file:
        try:
            with open(backup_file, "r") as f:
                backup_info = json.load(f)
            global mod_data, current_page, current_category, current_folder
            mod_data = backup_info["mods"]
            current_page = backup_info["current_page"]
            current_category = backup_info["current_category"]
            current_folder = backup_info["current_folder"]
            list_mods()
            messagebox.showinfo("Restore Complete", "Mod manager restored from backup.")
        except Exception as e:
            messagebox.showerror("Restore Error", f"An error occurred while restoring from backup: {str(e)}")

def rate_mod():
    """Allow users to rate a mod and provide a review."""
    selected_mod = mod_listbox.get(mod_listbox.curselection())
    if selected_mod:
        mod_name = selected_mod.split(" - ")[0]
        rating = simpledialog.askinteger("Rate Mod", f"Rate {mod_name} (1-5):", minvalue=1, maxvalue=5)
        if rating:
            review = simpledialog.askstring("Review Mod", f"Review {mod_name} (optional):")
            mod_data[mod_name]["ratings"].append(rating)
            if review:
                mod_data[mod_name]["reviews"].append(review)
            messagebox.showinfo("Rating Submitted", f"Thank you for rating {mod_name}!")

profiles = {"Default": []}

app = tk.Tk()
app.title("Zoo Tycoon 2 Mod Manager")

mod_listbox = tk.Listbox(app, width=70, height=15)
profile_combobox = ttk.Combobox(app, values=["All"] + list(profiles.keys()))
profile_combobox.set("Default")
profile_combobox.bind("<<ComboboxSelected>>", activate_profile)
install_button = tk.Button(app, text="Install Mod", command=install_mod)
prev_button = tk.Button(app, text="Previous Page", command=prev_page)
next_button = tk.Button(app, text="Next Page", command=next_page)
category_combobox = ttk.Combobox(app, values=["All", "Animals", "Scenery", "Gameplay"])
category_combobox.bind("<<ComboboxSelected>>", filter_category)
status_label = tk.Label(app, text="", fg="green")
check_updates_button = tk.Button(app, text="Check for Updates", command=check_for_updates)
check_conflicts_button = tk.Button(app, text="Check Conflicts", command=detect_conflicts)
backup_button = tk.Button(app, text="Backup Mods", command=backup_mods)
restore_button = tk.Button(app, text="Restore Mods", command=restore_mods)

sort_label = tk.Label(app, text="Sort by:")
sort_combobox = ttk.Combobox(app, values=["name", "description", "version", "category"])
sort_reverse_var = tk.BooleanVar()
sort_reverse_check = tk.Checkbutton(app, text="Reverse", variable=sort_reverse_var, command=sort_mods)

rate_button = tk.Button(app, text="Rate Mod", command=rate_mod)

create_profile_button = tk.Button(app, text="Create Profile", command=create_profile)
delete_profile_button = tk.Button(app, text="Delete Profile", command=delete_profile)

profile_combobox.pack(pady=5)
profile_combobox.set("All")
mod_listbox.pack(padx=10, pady=10)
install_button.pack()
prev_button.pack(side=tk.LEFT, padx=5, pady=5)
next_button.pack(side=tk.RIGHT, padx=5, pady=5)
category_combobox.pack()
status_label.pack(pady=5)
check_updates_button.pack()
check_conflicts_button.pack()
backup_button.pack()
restore_button.pack()
create_profile_button.pack(side=tk.LEFT, padx=5, pady=5)  # Create Profile button on the bottom left
delete_profile_button.pack(side=tk.LEFT, padx=5, pady=5)  # Delete Profile button on the bottom left
sort_label.pack()
sort_combobox.pack()
sort_reverse_check.pack()
rate_button.pack()

list_mods()

update_thread = threading.Thread(target=check_for_updates)
update_thread.daemon = True
update_thread.start()

app.mainloop()
