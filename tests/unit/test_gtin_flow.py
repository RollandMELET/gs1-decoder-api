"""
Tests TDD - phase RED pour la normalisation GTIN (AI 01).

Contexte : parse_gs1 valide le GTIN de l'AI 01 uniquement si sa valeur fait
déjà 14 chiffres. Un GTIN court fourni via le format lisible (01)... n'est ni
normalisé vers 14, ni validé. Ces tests définissent le comportement attendu
APRÈS la phase GREEN (normalisation + validation dans parse_gs1).
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
def test_ai01_gtin13_normalise_vers_14():
    """GTIN-13 fourni via (01)... doit être padé en 14 chiffres et validé."""
    items = parse_gs1("(01)4006381333931", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["value"] == "04006381333931", (
        f"Valeur attendue '04006381333931', obtenue '{gtin['value']}'"
    )
    assert gtin["valid"] is True, "GTIN valide - le chiffre de contrôle est correct"


@pytest.mark.unit
def test_ai01_gtin12_normalise_vers_14():
    """GTIN-12 fourni via (01)... doit être padé en 14 chiffres et validé."""
    items = parse_gs1("(01)036000291452", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["value"] == "00036000291452", (
        f"Valeur attendue '00036000291452', obtenue '{gtin['value']}'"
    )
    assert gtin["valid"] is True, "GTIN valide - le chiffre de contrôle est correct"


@pytest.mark.unit
def test_ai01_gtin13_invalide_detecte():
    """GTIN-13 avec chiffre de contrôle faux doit être rejeté après normalisation."""
    items = parse_gs1("(01)4006381333932", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["valid"] is False, (
        f"GTIN invalide - chiffre de contrôle faux, valid obtenu : {gtin['valid']}"
    )


@pytest.mark.unit
def test_ai01_gtin14_inchange():
    """NON-REGRESSION : GTIN-14 déjà correct doit rester identique et valide."""
    items = parse_gs1("(01)03760423190005", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["value"] == "03760423190005", (
        f"Valeur attendue '03760423190005', obtenue '{gtin['value']}'"
    )
    assert gtin["valid"] is True, "GTIN-14 valide - doit déjà passer"


@pytest.mark.unit
def test_ai01_concatene_14():
    """NON-REGRESSION : format concaténé 01<gtin14> doit rester identique et valide."""
    items = parse_gs1("0103760423190005", verbose=True)
    gtin = _item(items, "GTIN")
    assert gtin is not None, "L'item GTIN doit être présent"
    assert gtin["value"] == "03760423190005", (
        f"Valeur attendue '03760423190005', obtenue '{gtin['value']}'"
    )
    assert gtin["valid"] is True, "GTIN-14 valide - format concaténé doit déjà passer"
