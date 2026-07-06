"""Tests TDD - Lot B3 (phase RED) : alias courts GS1 Digital Link.

Couvre :
- Alias dans le chemin (gtin, ser, lot) -> conversion vers l'AI numérique correspondant.
- Alias dans la query (exp) -> idem.
- Préfixe de chemin custom sur domaine tiers (/products ignoré).
- is_digital_link avec alias seul (sans AI numérique).
- Sensibilité à la casse : "GTIN" en majuscules non reconnu.
- Non-régression : AI numériques purs inchangés.
"""
import pytest

from app.gs1_digital_link import is_digital_link, digital_link_to_gs1_string

GS = "\x1d"


# ---------------------------------------------------------------------------
# digital_link_to_gs1_string - alias
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_alias_path_gtin_ser():
    """gtin->01, ser->21 dans le chemin."""
    uri = "https://id.gs1.org/gtin/09521234543213/ser/XYZ"
    expected = "0109521234543213" + GS + "21XYZ"
    assert digital_link_to_gs1_string(uri) == expected


@pytest.mark.unit
def test_alias_path_lot():
    """lot->10 dans le chemin."""
    uri = "https://id.gs1.org/gtin/09521234543213/lot/ABC"
    expected = "0109521234543213" + GS + "10ABC"
    assert digital_link_to_gs1_string(uri) == expected


@pytest.mark.unit
def test_alias_query_exp():
    """exp->17 dans la query (AI numérique 01 dans le chemin, alias exp en query)."""
    uri = "https://id.gs1.org/01/09521234543213?exp=261231"
    expected = "0109521234543213" + GS + "17261231"
    assert digital_link_to_gs1_string(uri) == expected


@pytest.mark.unit
def test_prefixe_domaine_custom():
    """Préfixe /products sur domaine custom ignoré - on démarre au premier AI reconnu."""
    uri = "https://example.com/products/01/09521234543213/21/XYZ"
    expected = "0109521234543213" + GS + "21XYZ"
    assert digital_link_to_gs1_string(uri) == expected


# ---------------------------------------------------------------------------
# is_digital_link - alias
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_is_dl_alias_seul():
    """Digital Link avec alias seul (gtin) sans AI numérique : doit retourner True."""
    assert is_digital_link("https://id.gs1.org/gtin/09521234543213") is True


@pytest.mark.unit
def test_is_dl_casse_majuscule_rejetee():
    """Alias en majuscules (GTIN) non reconnu : is_digital_link doit retourner False."""
    assert is_digital_link("https://id.gs1.org/GTIN/09521234543213") is False


# ---------------------------------------------------------------------------
# Non-régression : AI numériques purs
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_numerique_inchange():
    """AI numériques dans le chemin - comportement existant préservé."""
    uri = "https://id.gs1.org/01/09521234543213/21/XYZ"
    expected = "0109521234543213" + GS + "21XYZ"
    assert digital_link_to_gs1_string(uri) == expected
