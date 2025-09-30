import pytest
from pathlib import Path
import xml.etree.ElementTree as Et
from zwift_3 import ZwiftPrefsManager

@pytest.fixture
def prefs_file(tmp_path:Path):
    """Creates temporary prefs file"""
    xml_path = tmp_path / "prefs.xml"
    root = Et.Element("ZWIFT")
    world = Et.SubElement(root, "WORLD")
    world.text = "2"
    tree = Et.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    return xml_path


def test_get_current_world(prefs_file):
    zpm = ZwiftPrefsManager()
    zpm.set_prefs_file(str(prefs_file))
    assert zpm.get_current_world() == 2