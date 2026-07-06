"""
Tests TDD - champ additif optionnel gtin14 (contrat API).

Phase RED : ces tests échouent tant que gtin14 n'est pas exposé.
Le champ gtin14 est renseigné UNIQUEMENT pour l'AI 01 (GTIN normalisé sur 14
chiffres), None sinon. Le mode simple (dict) reste inchangé. Additif, non cassant.
"""
import pytest

from app.gs1_parser import parse_gs1
from app.models import ParsedVerboseItem


def _item(items, name):
    for it in items:
        if it.get("name") == name:
            return it
    return None


@pytest.mark.unit
def test_gtin14_present_pour_ai01():
    """L'item GTIN (AI 01) porte le champ gtin14 = GTIN normalisé sur 14 chiffres."""
    items = parse_gs1("(01)4006381333931", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None
    assert gtin.get("gtin14") == "04006381333931"


@pytest.mark.unit
def test_gtin14_none_pour_autres_ai():
    """Les items non-GTIN portent gtin14 = None (champ présent, valeur nulle)."""
    items = parse_gs1("(10)ABC(21)XYZ", verbose=True)
    batch = _item(items, "BATCH")
    serial = _item(items, "SERIAL")
    assert batch is not None and serial is not None
    assert batch.get("gtin14") is None
    assert serial.get("gtin14") is None


@pytest.mark.unit
def test_mode_simple_inchange():
    """Le mode simple (verbose=False) reste un dict {name: value}, sans gtin14."""
    result = parse_gs1("(01)4006381333931")
    assert result == {"GTIN": "04006381333931"}


@pytest.mark.unit
def test_modele_accepte_gtin14_optionnel():
    """Le modèle ParsedVerboseItem expose gtin14 optionnel et le sérialise."""
    item = ParsedVerboseItem(
        ai="01", name="GTIN", value="04006381333931", valid=True, gtin14="04006381333931"
    )
    dump = item.model_dump()
    assert "gtin14" in dump
    assert dump["gtin14"] == "04006381333931"


@pytest.mark.unit
def test_modele_gtin14_defaut_none():
    """Rétro-compat : un item construit sans gtin14 a gtin14 = None."""
    item = ParsedVerboseItem(ai="10", name="BATCH", value="ABC", valid=True)
    assert item.gtin14 is None
