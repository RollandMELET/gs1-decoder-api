"""
Tests TDD - phase RED : intégration GS1 Digital Link dans parse_gs1.

Périmètre : parse_gs1 ne reconnaît pas encore les URI Digital Link.
Les tests 1-4 ÉCHOUENT jusqu'à la phase GREEN (lot B5).
Le test 5 (non-régression format concaténé) DOIT déjà passer.
"""
import pytest
from app.gs1_parser import parse_gs1


def _item(items, name):
    """Renvoie le dict de l'item dont le champ 'name' correspond, ou None."""
    for item in items:
        if item.get("name") == name:
            return item
    return None


@pytest.mark.unit
def test_dl_gtin_serial_verbose():
    """URI Digital Link avec GTIN-14 et numéro de série - mode verbose."""
    items = parse_gs1("https://id.gs1.org/01/09521234543213/21/XYZ", verbose=True)
    gtin = _item(items, "GTIN")
    serial = _item(items, "SERIAL")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["value"] == "09521234543213", (
        f"Valeur GTIN attendue '09521234543213', obtenue '{gtin['value'] if gtin else None}'"
    )
    assert serial is not None, "L'item SERIAL doit être présent"
    assert serial["value"] == "XYZ", (
        f"Valeur SERIAL attendue 'XYZ', obtenue '{serial['value'] if serial else None}'"
    )


@pytest.mark.unit
def test_dl_gtin13_normalise_et_valide():
    """URI Digital Link avec GTIN-13 - doit être paddé à 14 chiffres et validé (couvre lot B4)."""
    items = parse_gs1("https://id.gs1.org/01/4006381333931", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["value"] == "04006381333931", (
        f"Valeur attendue '04006381333931' (paddée), obtenue '{gtin['value'] if gtin else None}'"
    )
    assert gtin["valid"] is True, "Le chiffre de contrôle du GTIN doit être valide"
    assert gtin["gtin14"] == "04006381333931", (
        f"gtin14 attendu '04006381333931', obtenu '{gtin['gtin14'] if gtin else None}'"
    )


@pytest.mark.unit
def test_dl_alias_mode_simple():
    """URI Digital Link avec alias courts (gtin, lot) - mode simple (verbose=False)."""
    result = parse_gs1("https://id.gs1.org/gtin/09521234543213/lot/ABC")
    assert result == {"GTIN": "09521234543213", "BATCH": "ABC"}, (
        f"Résultat attendu {{'GTIN': '09521234543213', 'BATCH': 'ABC'}}, obtenu {result}"
    )


@pytest.mark.unit
def test_dl_domaine_custom():
    """URI Digital Link sur un domaine personnalisé - le host ne doit pas bloquer le parsing."""
    items = parse_gs1("https://example.com/products/01/09521234543213/21/XYZ", verbose=True)
    gtin = _item(items, "GTIN")
    serial = _item(items, "SERIAL")
    assert gtin is not None, "L'item GTIN doit être présent même avec un domaine custom"
    assert gtin["value"] == "09521234543213", (
        f"Valeur GTIN attendue '09521234543213', obtenue '{gtin['value'] if gtin else None}'"
    )
    assert serial is not None, "L'item SERIAL doit être présent même avec un domaine custom"
    assert serial["value"] == "XYZ", (
        f"Valeur SERIAL attendue 'XYZ', obtenue '{serial['value'] if serial else None}'"
    )


@pytest.mark.unit
def test_concatene_non_dl_inchange():
    """Non-régression : format concaténé classique toujours parsé correctement."""
    items = parse_gs1("0103760423190005", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent pour le format concaténé"
    assert gtin["value"] == "03760423190005", (
        f"Valeur attendue '03760423190005', obtenue '{gtin['value'] if gtin else None}'"
    )
