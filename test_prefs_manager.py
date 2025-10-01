import pytest
from pathlib import Path
import xml.etree.ElementTree as Et
from zwift_3 import ZwiftPrefsManager, WorldSelectorUI
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
def wui(zpm: ZwiftPrefsManager) -> WorldSelectorUI:
    """Returns a WorldSelectorUI object"""
    return WorldSelectorUI(pref_manager=zpm)

def test_get_current_world(prefs_file: Path, zpm: ZwiftPrefsManager, fake_mem: Path) -> None:
    """Tests if the world is being read correctly from prefs.xml"""
    zpm.set_prefs_file(str(prefs_file))
    assert zpm.get_current_world() == 2

def test_writes_file(fake_mem: Path, prefs_file: Path, zpm: ZwiftPrefsManager) -> None:
    """Tests if the prefs path is being writen correctly into memory"""
    zpm.set_prefs_file(str(prefs_file))
    assert fake_mem.read_text(encoding="utf-8").strip() == str(prefs_file.resolve())

def test_get_world_name(wui: WorldSelectorUI) -> None:
    """Tests if the get_world_name can get world name from world id"""
    assert wui.get_world_name(5) == "Innsbruck"

def test_set_world(prefs_file: Path, zpm: ZwiftPrefsManager) -> None:
    zpm.set_prefs_file(str(prefs_file))
    zpm.set_world(3)
    assert zpm.get_current_world() == 3
    zpm.set_world(2)
    assert zpm.get_current_world() == 2
