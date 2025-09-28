# import sys
import logging
import xml.etree.ElementTree as Et
from pathlib import Path
# from PIL import Image
import customtkinter as ctk
from tkinter import filedialog


#--------------   Settings   ------------------
STS_LBL_FONT = ("Arial", 22, "bold")
STS_LBL_TXT_CLR = "#005B96"
BTN_FONT = ("Arial", 20, "bold")
BTN_FG = "#FF6600"
BTN_HOVER = "#FFA500"
HEADER_CLR = "white"
HEADER_FONT = ("Arial", 20, "bold")
# ----------------- Logging -----------------
logging.basicConfig(
    filename="zwift_world_selector.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
# ----------------- Utility -----------------
# def resource_path(filename: str) -> str:
#     """Get path to resource, works in dev and PyInstaller bundle."""
#     base_path = getattr(sys, "_MEIPASS", Path(".").resolve())
#     return str(Path(base_path) / filename)
ico_path = Path("zwift_logo.ico")
# ----------------- Prefs Manager -----------------
class ZwiftPrefsManager:
    def __init__(self):
        self.possible_paths = [
            Path("~/Documents/Zwift/prefs.xml").expanduser(),  # Windows
            Path("~/Library/Application Support/Zwift/prefs.xml").expanduser(),  # macOS
            Path("~/.local/share/Zwift/prefs.xml").expanduser(),  # Linux
        ]
        self.prefs_path = self._find_prefs()

    def _find_prefs(self) -> Path:
        for path in self.possible_paths:
            if path.exists():
                return path
        return None

    def set_prefs_file(self, filepath: str) -> None:
        self.prefs_path = Path(filepath)

    def get_current_world(self) -> int | None:
        if not self.prefs_path:
            return None
        try:
            tree = Et.parse(self.prefs_path)
            root = tree.getroot()
            elem = root.find("WORLD")
            return int(elem.text) if elem is not None else None
        except Exception as e:
            logging.error(f"Error reading prefs.xml: {e}")
            return None

    def set_world(self, world_id: int) -> bool:
        if not self.prefs_path:
            return False
        try:
            tree = Et.parse(self.prefs_path)
            root = tree.getroot()
            elem = root.find("WORLD")
            elem.text = str(world_id)
            tree.write(self.prefs_path)
            return True
        except Exception as e:
            logging.error(f"Error writing prefs.xml: {e}")
            return False
# ----------------- GUI -----------------
class WorldSelectorUI(ctk.CTk):
    WORLDS = {
        "Watopia": 1,
        "Richmond": 2,
        "London": 3,
        "New York": 4,
        "Innsbruck": 5,
        "Yorkshire": 7,
        "Makuri Islands": 9,
        "France": 10,
        "Paris": 11,
        "Scotland": 13,
    }

    def __init__(self, pref_manager: ZwiftPrefsManager):
        super().__init__()
        self.prefs_manager = pref_manager

        self.title("Zwift World Selector")
        self.geometry("420x600")
        self.resizable(0, 0)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Icon
        try:
            self.iconbitmap(ico_path)  # Better than PNG for Windows
        except Exception as e:
            logging.warning(f"Could not set window icon: {e}")

        # Header
        header = ctk.CTkFrame(self, fg_color="#0072c6", corner_radius=0)
        header.pack(fill="x")

        label = ctk.CTkLabel(
            header,
            text="Zwift World Selector",
            font=HEADER_FONT,
            text_color=HEADER_CLR,
        )
        label.pack(side="left", padx=10, pady=15)

        # donate_btn = ctk.CTkButton(
        #     header,
        #     text="Donate",
        #     fg_color="#ff8c00",
        #     command=self.open_donate_window,
        # )
        # donate_btn.pack(side="right", padx=10, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self,
                                         text="",
                                         wraplength=350,
                                         font=STS_LBL_FONT,
                                         text_color=STS_LBL_TXT_CLR)
        self.status_label.pack(pady=15)

        # World buttons
        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(pady=15)

        row, col = 0, 0
        for world_name, world_id in self.WORLDS.items():
            btn = ctk.CTkButton(
                grid_frame,
                text=world_name,
                font=BTN_FONT,
                fg_color=BTN_FG,
                hover_color=BTN_HOVER,
                width=160,
                height=40,
                command=lambda wid=world_id: self.on_world_select(wid),
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 1:
                col = 0
                row += 1

        # Select file button
        select_btn = ctk.CTkButton(self,
                                   text="Select prefs.xml file",
                                   font=BTN_FONT,
                                   fg_color="#0072c6",
                                   command=self.select_prefs_file)
        select_btn.pack(pady=15)

        # Exit button
        exit_btn = ctk.CTkButton(self,
                                 text="Exit",
                                 fg_color="#dc3545",
                                 command=self.destroy,
                                 font=BTN_FONT)
        exit_btn.pack(pady=20)

        # Highlight current world (if any)
        self.highlight_current_world()

    def update_status(self, message: str, color: str = "#005B96"):
        self.status_label.configure(text=message, text_color=color)

    def select_prefs_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Zwift prefs.xml file",
            filetypes=[("XML files", "*.xml")],
        )
        if file_path:
            self.prefs_manager.set_prefs_file(file_path)
            self.update_status("Prefs file selected!", "green")
            self.after(2500, self.highlight_current_world)

    def on_world_select(self, world_id: int) -> None:
        if self.prefs_manager.set_world(world_id):
            self.update_status(f"World changed to: {self.get_world_name(world_id)}", "green")
            self.after(2500, self.highlight_current_world)
        else:
            self.update_status("Failed to update prefs.xml", "red")

    def highlight_current_world(self):
        current = self.prefs_manager.get_current_world()
        if current:
            name = self.get_world_name(current)
            self.update_status(f"Current world: {name}", STS_LBL_TXT_CLR)

    def get_world_name(self, wid: int) -> str:
        return next((name for name, num in self.WORLDS.items() if num == wid), str(wid))

    # def open_donate_window(self):
    #     win = ctk.CTkToplevel(self)
    #     win.title("Donate")
    #     win.geometry("300x400")
    #
    #     msg = ctk.CTkLabel(
    #         win, text="Support this project by donating!", font=ctk.CTkFont(size=14, weight="bold")
    #     )
    #     msg.pack(pady=10)
    #
    #     try:
    #         img = Image.open(resource_path("Donation.png"))
    #         img = img.resize((200, 250))
    #         photo = ctk.CTkImage(img, size=(200, 250))
    #         qr = ctk.CTkLabel(win, image=photo, text="")
    #         qr.pack(pady=20)
    #     except Exception as e:
    #         logging.error(f"Error loading QR code: {e}")
    #         placeholder = ctk.CTkLabel(win, text="(QR Code not available)")
    #         placeholder.pack(pady=20)
    #
    #     close_btn = ctk.CTkButton(win, text="Close", command=win.destroy)
    #     close_btn.pack(pady=10)
# ----------------- Run -----------------
if __name__ == "__main__":
    prefs_manager = ZwiftPrefsManager()
    app = WorldSelectorUI(prefs_manager)
    app.mainloop()
