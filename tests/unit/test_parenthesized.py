"""
Tests TDD - Phase RED : format GS1 parenthésé (AI)valeur(AI)valeur...
Ces tests prouvent le bug de parsing des parenthèses et passeront après correction de parse_gs1.
"""
import pytest
from app.gs1_parser import parse_gs1


def _val(items, name):
    """Extraire une valeur par nom depuis la liste verbose."""
    return next((it["value"] for it in items if it["name"] == name), None)


@pytest.mark.unit
def test_parenthese_gtin_propre():
    """(01)03760423190005 - la valeur GTIN doit être 14 chiffres propres, sans parenthèse ni chiffre perdu."""
    items = parse_gs1("(01)03760423190005", verbose=True)
    assert _val(items, "GTIN") == "03760423190005"


@pytest.mark.unit
def test_parenthese_deux_ai_variables():
    """(10)ABC(21)XYZ - BATCH = ABC, SERIAL = XYZ ; le BATCH ne doit PAS avaler 21XYZ."""
    items = parse_gs1("(10)ABC(21)XYZ", verbose=True)
    assert _val(items, "BATCH") == "ABC"
    assert _val(items, "SERIAL") == "XYZ"


@pytest.mark.unit
def test_parenthese_mode_simple():
    """Mode verbose=False : retourne un dict {name: value} correctement découpé."""
    result = parse_gs1("(10)ABC(21)XYZ")
    assert result == {"BATCH": "ABC", "SERIAL": "XYZ"}


@pytest.mark.unit
def test_parenthese_gtin_valide():
    """Après correction, le chiffre de contrôle du GTIN 03760423190005 doit être valide (valid=True)."""
    items = parse_gs1("(01)03760423190005", verbose=True)
    gtin_item = next((it for it in items if it["name"] == "GTIN"), None)
    assert gtin_item is not None
    assert gtin_item["valid"] is True


@pytest.mark.unit
def test_concatene_inchange():
    """NON-RÉGRESSION : le format concaténé sans parenthèses doit continuer de fonctionner."""
    items = parse_gs1("0103760423190005", verbose=True)
    assert _val(items, "GTIN") == "03760423190005"
