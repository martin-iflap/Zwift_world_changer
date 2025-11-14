import pytest
from pathlib import Path
import xml.etree.ElementTree as Et
from zwift_3 import ZwiftPrefsManager, WorldSelectorUI,  ZwiftInsiderScraper
import zwift_3


@pytest.fixture
def prefs_file(tmp_path: Path) -> Path:
    """Creates temporary prefs file"""
    xml_path = tmp_path / "prefs.xml"
    root = Et.Element("ZWIFT")
    world = Et.SubElement(root, "WORLD")
    world.text = "2"
    tree = Et.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    return xml_path

@pytest.fixture
def fake_mem(tmp_path, monkeypatch) -> Path:
    """Creates a temporary memory.txt file"""
    fake_mem = tmp_path / "memory.txt"
    monkeypatch.setattr(zwift_3, "MEMORY", fake_mem)
    return fake_mem

@pytest.fixture
def zpm() -> ZwiftPrefsManager:
    """Returns a ZwiftPrefsManager object"""
    return ZwiftPrefsManager()

@pytest.fixture
def zi_scraper(zpm: ZwiftPrefsManager) -> ZwiftInsiderScraper:
    """Returns a ZwiftInsiderScraper object"""
    return ZwiftInsiderScraper(zpm)

@pytest.fixture
def wui(zpm: ZwiftPrefsManager, scraper: ZwiftInsiderScraper) -> WorldSelectorUI:
    """Returns a WorldSelectorUI object"""
    return WorldSelectorUI(pref_manager=zpm, scrape_manager=scraper)

def test_get_current_world(prefs_file: Path, zpm: ZwiftPrefsManager, fake_mem: Path) -> None:
    """Test if the world is being read correctly from prefs.xml"""
    zpm.set_prefs_file(str(prefs_file))
    assert zpm.get_current_world() == 2

def test_reads_from_mem(prefs_file: Path,
                        zpm: ZwiftPrefsManager,
                        fake_mem: Path,
                        monkeypatch) -> None:
    """Test if the _find_prefs can read from memory.txt"""
    monkeypatch.setattr(zpm, "possible_paths", [])
    fake_mem.write_text(str(prefs_file), encoding="utf-8")
    assert zpm._find_prefs() == prefs_file

def test_writes_to_mem(fake_mem: Path, prefs_file: Path, zpm: ZwiftPrefsManager) -> None:
    """Test if the prefs path is being writen correctly into memory.txt"""
    zpm.set_prefs_file(str(prefs_file))
    assert fake_mem.read_text(encoding="utf-8").strip() == str(prefs_file.resolve())

def test_set_world(prefs_file: Path, zpm: ZwiftPrefsManager, fake_mem: Path) -> None:
    """Test if the world is being set properly inside prefs.xml"""
    zpm.set_prefs_file(str(prefs_file))
    zpm.set_world(3)
    assert zpm.get_current_world() == 3

    zpm.set_world(5)
    tree = Et.parse(prefs_file)
    root = tree.getroot()
    assert int(root.find("WORLD").text) == 5

    assert zpm.set_world(99) is False

def test_get_world_name(zpm: ZwiftPrefsManager) -> None:
    """Test if the get_world_name can get world name from world id"""
    assert zpm.get_world_name(5) == "Innsbruck"
    assert zpm.get_world_name(99) is None


def test_get_world_rotation(zi_scraper: ZwiftInsiderScraper, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test if the get_world_rotation can get the world that's on rotation from the scraped data"""
    monkeypatch.setattr(zi_scraper, "get_current_day", lambda: "8")
    fetched_data = [
     'October 27, 2025', 'LAST UPDATED', 'October 27, 2025', '8',
     'Watopia is available every day while the other maps rotate as “Guest Worlds” according to the calendar below. This gives Zwifters access to three worlds (',
     'Watopia', '+ two guest worlds) at any given time.', '<', 'November 2025', '>', 'Monday', 'Tuesday', 'Wednesday',
     'Thursday', 'Friday', 'Saturday', 'Sunday', '1', 'Makuri Islands', 'Makuri Islands', 'New York', 'New York', '2',
     'Makuri Islands', 'Makuri Islands', 'New York', 'New York', '3', 'Makuri Islands', 'Makuri Islands', 'New York',
     'New York', '4', 'Makuri Islands', 'Makuri Islands', 'New York', 'New York', '5', 'Makuri Islands',
     'Makuri Islands', 'New York', 'New York', '6', 'Makuri Islands', 'Makuri Islands', 'New York', 'New York', '7',
     'Makuri Islands', 'Makuri Islands', 'New York', 'New York', '8', 'Innsbruck', 'Innsbruck', 'New York',
     'New York', '9', 'Makuri Islands', 'Makuri Islands', 'New York', 'New York'
    ]

    rotation = zi_scraper.get_world_rotation(lines=fetched_data)
    assert len(rotation) == 2
    assert rotation == ["Innsbruck", "New York"]
