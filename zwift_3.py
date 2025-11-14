import xml.etree.ElementTree as Et
from tkinter import filedialog
from bs4 import BeautifulSoup
import customtkinter as ctk
from pathlib import Path
from lxml import etree
import requests
import datetime
import logging
import re
# from PIL import Image
# import sys


#--------------   Settings   ------------------
STS_LBL_FONT = ("Arial", 22, "bold")
STS_LBL_TXT_CLR = "#005B96"
BTN_FONT = ("Arial", 20, "bold")
BTN_FG = "#FF6600"
BTN_HOVER = "#FFA500"
HEADER_CLR = "white"
HEADER_FONT = ("Arial", 20, "bold")

MEMORY = Path("memory.txt")
BASE_URL = "https://zwiftinsider.com/schedule/"
# ----------------- Logging -----------------
logging.basicConfig(filename="zwift_world_selector.log",
                    level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
# ----------------- ICO Path -----------------
# def resource_path(file_name: str) -> Path:
#     """Get path to resource, works in dev and PyInstaller bundle"""
#     try:
#         base_path = getattr(sys, "_MEIPASS", Path(".").resolve())
#         return Path(base_path) / file_name
#     except Exception as e:
#         logging.error(f"Getting icon path failed: {e}")
ico_path = Path("zwift_logo.ico")
# ----------------- Prefs Manager -----------------
class ZwiftPrefsManager:

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

    def __init__(self):
        self.possible_paths = [
            Path("~/Documents/Zwift/prefs.xml").expanduser(),  # Windows
            Path("~/Library/Application Support/Zwift/prefs.xml").expanduser(),  # macOS
            Path("~/.local/share/Zwift/prefs.xml").expanduser(),  # Linux
        ]
        self.prefs_path = self._find_prefs()

    def _find_prefs(self) -> Path | None:
        """Function will look for prefs.xml path in possible paths
        and if None exists it will try to load absolute path from memory"""
        for path in self.possible_paths:
            if path.exists():
                return path
        try:
            with open(MEMORY, "r", encoding="utf-8") as f:
                content = Path(f.read().strip())
                return content if content.exists() else None
        except Exception as e:
            logging.error(f"Error reading memory file: {e}")

    def set_prefs_file(self, filepath: str) -> None:
        filepath = str(Path(filepath).resolve())
        self.prefs_path = Path(filepath)
        try:
            with open(MEMORY, "w", encoding="utf-8") as f:
                f.write(filepath)
        except Exception as e:
            logging.error(f"Error writing into memory: {e}")
            return None

    def get_current_world(self) -> int | None:
        """Read prefs.xml and return the ID of the currently selected world.

        Returns:
            int | None: The world ID if found, otherwise None.
        """
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
        """Changes the text of the WORLD element to the currently selected world ID.
            Firstly a .tmp file is created and updated.
            The .tmp file than replaces the original prefs.xml to prevent file corruption.

            Returns:
                True | False: If succeeded, otherwise False
            """
        if not self.prefs_path:
            return False
        if self.get_world_name(world_id) is None:
            return False
        try:
            parser = etree.XMLParser(remove_blank_text=False)
            tree = etree.parse(str(self.prefs_path), parser)
            root = tree.getroot()
            elem = root.find("WORLD")
            if elem is None:
                logging.warning("prefs.xml has no WORLD element")
                return False
            elem.text = str(world_id)
            temp_path = self.prefs_path.with_suffix(".tmp")
            tree.write(temp_path, encoding="utf-8", xml_declaration=True, pretty_print=True)
            temp_path.replace(self.prefs_path)
            return True
        except Exception as e:
            logging.error(f"Error writing prefs.xml: {e}")
            return False

    def get_world_name(self, wid: int) -> str:
        w_name = next((name for name, num in self.WORLDS.items() if num == wid), None)
        if w_name is None:
            logging.error(f"The world number {wid} doesn't exist!")
            return w_name
        return w_name
# ----------------- GUI -----------------
class WorldSelectorUI(ctk.CTk):
    def __init__(self, pref_manager: ZwiftPrefsManager, scrape_manager):
        super().__init__()
        self.prefs_manager = pref_manager
        self.scraper = scrape_manager

        self.title("Zwift World Selector")
        self.geometry("420x620")
        self.resizable(0, 0)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Icon
        try:
            self.iconbitmap(ico_path)  # Better than PNG for Windows
        except Exception as e:
            logging.warning(f"Could not set window icon: {e}")

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
        if self.prefs_manager.prefs_path is None:
            self.status_label.configure(text="Please select prefs.xml file manually", text_color="red")
        else:
            self.status_label.configure(text="Prefs file found✔️", text_color="green")

        rotation_text = self.get_rotation_txt()
        self.rotation_label = ctk.CTkLabel(self,
                                           wraplength=350,
                                           text=rotation_text,
                                           font=STS_LBL_FONT,
                                           text_color=STS_LBL_TXT_CLR)
        self.rotation_label.pack(pady=10)

        # World buttons
        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(pady=15)

        row, col = 0, 0
        for world_name, world_id in prefs_manager.WORLDS.items():
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

        select_btn = ctk.CTkButton(self,
                                   text="Select prefs.xml file",
                                   font=BTN_FONT,
                                   fg_color="#0072c6",
                                   command=self.select_prefs_file)
        select_btn.pack(pady=15)

        exit_btn = ctk.CTkButton(self,
                                 text="Exit",
                                 fg_color="#dc3545",
                                 command=self.destroy,
                                 font=BTN_FONT)
        exit_btn.pack(pady=20)

        # Highlight current world (if any)
        self.after(2500, self.highlight_current_world)

    def update_status(self, message: str, color: str = "#005B96"):
        self.status_label.configure(text=message, text_color=color)

    def select_prefs_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Zwift prefs.xml file",
            filetypes=[("XML files", "*.xml")],
        )
        if file_path:
            self.prefs_manager.set_prefs_file(file_path)
            self.update_status("Prefs file selected✔️", "green")
            self.after(2500, self.highlight_current_world)

    def on_world_select(self, world_id: int) -> None:
        """calls the set_world function that changes the current world and updates status label"""
        if self.prefs_manager.set_world(world_id):
            self.update_status(f"World changed to: {prefs_manager.get_world_name(world_id)}", "green")
            self.after(2500, self.highlight_current_world)
        else:
            self.update_status("Failed to update prefs.xml (prefs.xml might be invalid)", "red")

    def highlight_current_world(self):
        """Highlights the currently selected world in the status label"""
        current = self.prefs_manager.get_current_world()
        if current:
            name = prefs_manager.get_world_name(current)
            self.update_status(f"Current world: {name}", STS_LBL_TXT_CLR)
        else:
            self.update_status("No world selected", "red")

    def get_rotation_txt(self):
        today_worlds = self.scraper.run_main_scraper()
        if today_worlds:
            return f"Rotation worlds: \n {today_worlds[0]} {today_worlds[1]}"
        else:
            return "Not found"


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
# --------------------   Scrape Zwift insider   --------------------
class ZwiftInsiderScraper:
    def __init__(self, manager: ZwiftPrefsManager):
        self.manager = manager

    def get_current_day(self) -> str:
        """Get the current day of the month as str"""
        return str(datetime.date.today().day)

    def fetch_html(self, url: str=BASE_URL) -> str | None:
        """Fetch HTML content from a URL"""
        try:
            headers  = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://zwiftinsider.com/",
        "Connection": "close"}
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            logging.info(f"Successfully fetched HTML content from {url}")
            return response.text
        except Exception as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return None

    def pull_from_html(self) -> list[str] | None:
        """Scrape data form Zwift Insider schedule page"""
        html_content = self.fetch_html()
        if not html_content:
            return None

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            content = soup.select_one("article .entry-content") or soup
            text = "\n".join(content.stripped_strings)
            lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()] # take a look at this later
            logging.info("Successfully parsed HTML content")
            return lines
        except Exception as e:
            logging.error(f"Error parsing HTML content: {e}")
            return None

    def get_world_rotation(self, lines: list[str]) -> list | list[str]:
        """Get the current worlds from the scraped data = world rotation"""
        today = self.get_current_day()
        day_rx = re.compile(rf"^\s*0*{today}\s*$")
        idx = None
        for i, line in enumerate(lines):
            if day_rx.match(line):
                idx = i
                logging.info(f"Found current day in the schedule on index {i}")
                break

        if idx is None:
            logging.error("Could not find current day in the schedule")
            return []

        window = lines[idx: idx + 4]
        found = []
        for ln in window:
            for w in self.manager.WORLDS.keys():
                if re.search(rf"\b{re.escape(w)}\b", ln, re.IGNORECASE):
                    if w not in found:
                        found.append(w)
        logging.info(f"World rotation found for today: {found}")
        return found

    def run_main_scraper(self):
        """Main function to run the scraper and get today's world rotation"""
        html_lines = scraper.pull_from_html()
        if html_lines:
            today_rotation = scraper.get_world_rotation(html_lines)
            return today_rotation
        else:
            logging.error("Failed to retrieve today's world rotation")
            return []




# ----------------- Run -----------------
if __name__ == "__main__":
    prefs_manager = ZwiftPrefsManager()
    scraper = ZwiftInsiderScraper(prefs_manager)
    app = WorldSelectorUI(prefs_manager, scraper)
    app.mainloop()
