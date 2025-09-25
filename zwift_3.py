import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import os


def create_world_selector():
    # Create main window
    root = tk.Tk()
    root.title("Zwift World Selector")
    root.geometry("400x600")
    root.configure(bg="#f4f4f4")

    # Common Zwift prefs.xml locations
    possible_paths = [
        os.path.expanduser("~/Documents/Zwift/prefs.xml"),  # Windows default
        os.path.expanduser("~/Library/Application Support/Zwift/prefs.xml"),  # Mac default
        os.path.expanduser("~/.local/share/Zwift/prefs.xml")  # Linux default
    ]

    # Initialize prefs path
    prefs_path = None
    for path in possible_paths:
        if os.path.exists(path):
            prefs_path = path
            break

    # Create header
    header_frame = tk.Frame(root, bg="#0072c6")
    header_frame.pack(fill="x")

    header_label = tk.Label(
        header_frame, text="Zwift World Selector", font=("Arial", 18, "bold"),
        fg="white", bg="#0072c6", pady=10
    )
    header_label.pack()

    # Instructions / Status area
    status_label = tk.Label(
        root, text="Please select a world",
        font=("Arial", 12), bg="#f4f4f4", wraplength=350, justify="center"
    )
    status_label.pack(pady=20)

    def update_status(message, color="black"):
        status_label.config(text=message, fg=color)

    def select_prefs_file():
        nonlocal prefs_path
        file_path = filedialog.askopenfilename(
            title="Select Zwift prefs.xml file",
            filetypes=[("XML files", "*.xml")]
        )
        if file_path:
            prefs_path = file_path
            update_status(f"Prefs file selected: {os.path.basename(file_path)}", "green")
        else:
            update_status("No file selected. Please try again.", "red")


    def on_world_select(world_num):
        if not prefs_path:
            update_status("Error: prefs.xml file not found. Please select it manually.", "red")
            return

        try:
            # Parse the XML file
            tree = ET.parse(prefs_path)
            prefs_root = tree.getroot()

            # Find or create the WORLD element and update its value
            world_elem = prefs_root.find("WORLD")
            if world_elem is None:
                world_elem = ET.SubElement(prefs_root, "WORLD")
            world_elem.text = str(world_num)

            tree.write(prefs_path)
            update_status(f"World successfully changed to World {selected_world}!", "green")
        except Exception as e:
            update_status(f"Error updating prefs.xml: {str(e)}", "red")

    # Create the world buttons
    worlds = {
        "Watopia": 1,
        "Richmond": 2,
        "London": 3,
        "New York": 4,
        "Innsbruck": 5,
        "Yorkshire": 7,
        "Makuri Islands": 9,
        "France": 10,
        "Paris": 11,
        "Scotland": 13
    }


    button_frame = tk.Frame(root, bg="#f4f4f4")
    button_frame.pack(pady=10)

    row, col = 0, 0
    for world_name, world_num in worlds.items():
        btn = tk.Button(
            button_frame,
            text=world_name,
            font=("Arial", 12, "bold"),
            bg="#ff8c00",
            fg="white",
            width=16,
            height=2,
            relief="flat",
            command=lambda wn=world_num: on_world_select(wn)
        )
        btn.grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col > 1:  # Two buttons per row
            col = 0
            row += 1



    # Add "Select prefs.xml" button
    select_file_btn = tk.Button(
        root,
        text="Select prefs.xml file",
        font=("Arial", 12, "bold"),
        bg="#0072c6",
        fg="white",
        relief="flat",
        command=select_prefs_file
    )
    select_file_btn.pack(pady=10)

    # Add "Exit" button
    exit_button = tk.Button(
        root,
        text="Exit",
        font=("Arial", 12, "bold"),
        bg="#dc3545",
        fg="white",
        relief="flat",
        command=root.destroy
    )
    exit_button.pack(pady=10)

    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    create_world_selector()
