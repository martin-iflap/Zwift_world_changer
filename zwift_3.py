import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import os
import sys
import logging
from PIL import Image, ImageTk

# Setup logging
# logging.basicConfig(filename="error.log", level=logging.ERROR)
# logging.basicConfig(level=logging.ERROR)

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_world_selector():
    # Create main window
    root = tk.Tk()
    root.tk.call('tk', 'scaling', 1.5)  # Adjust scaling for consistent appearance
    icon_path = resource_path('zwift_logo.png')
    try:
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
    except Exception as e:
        logging.error(f"Error loading icon: {e}")

    root.title("Zwift World Selector")
    root.geometry("400x600")
    root.configure(bg="#f4f4f4")

    possible_paths = [
        os.path.expanduser("~/Documents/Zwift/prefs.xml"),  # Windows default
        os.path.expanduser("~/Library/Application Support/Zwift/prefs.xml"),  # Mac default
        os.path.expanduser("~/.local/share/Zwift/prefs.xml")  # Linux default
    ]

    prefs_path = None
    for path in possible_paths:
        if os.path.exists(path):
            prefs_path = path
            break

    # Create header with Donate button
    header_frame = tk.Frame(root, bg="#0072c6")
    header_frame.pack(fill="x")

    header_label = tk.Label(header_frame, text="Zwift World Selector", font=("Arial", 18, "bold"),
                            fg="white", bg="#0072c6", pady=10)
    header_label.pack(side="left", padx=10)

    def open_donate_window():
        # Create the donation window
        donate_window = tk.Toplevel(root)
        try:
            donate_icon = tk.PhotoImage(file=icon_path)
            donate_window.iconphoto(True, donate_icon)
        except Exception as e:
            logging.error(f"Error loading donate window icon: {e}")

        donate_window.title("Donate")
        donate_window.geometry("300x440")
        donate_window.configure(bg="#f4f4f4")

        # Add message
        message_label = tk.Label(donate_window, text="Support this project by donating!", font=("Arial", 14, "bold"),
                                 bg="#f4f4f4", wraplength=280, justify="center")
        message_label.pack(pady=10)

        # Load and resize the QR code
        qr_path = resource_path('Donation.png')
        try:
            qr_image = Image.open(qr_path)
            resized_qr = qr_image.resize((200, 250))  # Adjust size as needed (in pixels)
            qr_photo = ImageTk.PhotoImage(resized_qr)
            qr_label = tk.Label(donate_window, image=qr_photo, bg="#f4f4f4")
            qr_label.image = qr_photo  # Keep a reference to avoid garbage collection
            qr_label.pack(pady=20)
        except Exception as e:
            logging.error(f"Error loading or resizing QR code image: {e}")
            qr_placeholder = tk.Label(donate_window, text="(QR Code not available)", font=("Arial", 12, "italic"),
                                      bg="#d9d9d9", fg="#555555", width=25, height=12, relief="solid")
            qr_placeholder.pack(pady=20)

        # Close button for donation window
        close_button = tk.Button(donate_window, text="Close", font=("Arial", 12, "bold"),
                                 bg="#0072c6", fg="white", relief="flat", command=donate_window.destroy)
        close_button.pack(pady=10)

    donate_button = tk.Button(header_frame, text="Donate", font=("Arial", 10, "bold"),
                               bg="#ff8c00", fg="white", relief="flat", command=open_donate_window)
    donate_button.pack(side="right", padx=10, pady=10)

    # Instructions / Status area
    status_label = tk.Label(root, text="Please select a world",
                            font=("Arial", 12), bg="#f4f4f4", wraplength=350, justify="center")
    status_label.pack(pady=20)

    def update_status(message, color="black"):
        status_label.config(text=message, fg=color)

    def select_prefs_file():
        nonlocal prefs_path
        file_path = filedialog.askopenfilename(title="Select Zwift prefs.xml file",
                                               filetypes=[("XML files", "*.xml")])
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
            update_status(f"World successfully changed to {worlds_reversed[world_num]}!", "green")
        except Exception as e:
            logging.error(f"Error updating prefs.xml: {e}")
            update_status(f"Error updating prefs.xml: {str(e)}", "red")

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

    worlds_reversed = {v: k for k, v in worlds.items()}

    button_frame = tk.Frame(root, bg="#f4f4f4")
    button_frame.pack(pady=10)

    row, col = 0, 0
    for world_name, world_num in worlds.items():
        btn = tk.Button(button_frame, text=world_name, font=("Arial", 12, "bold"),
                        bg="#ff8c00", fg="white", activebackground="#ff8c00",
                        activeforeground="#0072c6", width=16, height=2, relief="flat",
                        command=lambda wn=world_num: on_world_select(wn))
        btn.grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col > 1:  # Two buttons per row
            col = 0
            row += 1

    select_file_btn = tk.Button(root, text="Select prefs.xml file", font=("Arial", 12, "bold"),
                                bg="#0072c6", fg="white", relief="flat", command=select_prefs_file)
    select_file_btn.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", font=("Arial", 12, "bold"),
                            bg="#dc3545", fg="white", relief="flat", command=root.destroy)
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
