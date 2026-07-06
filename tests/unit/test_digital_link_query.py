"""
Tests unitaires - GS1 Digital Link parser (lot B2, phase RED)
Périmètre : query string (data attributes numériques) et décodage pourcent
(path + query). La GREEN est réservée au lot B2 - ces tests échouent
intentionnellement jusqu'à l'implémentation.
"""
import pytest
from app.gs1_digital_link import digital_link_to_gs1_string

GS = "\x1d"


@pytest.mark.unit
def test_query_data_attributes_numeriques():
    """Query string avec AI numériques (?17=...&10=...) ajoutés après le path.

    Le path donne le GTIN-14, la query ajoute 17 puis 10 dans l'ordre d'apparition.
    """
    result = digital_link_to_gs1_string(
        "https://id.gs1.org/01/09521234543213?17=261231&10=LOT"
    )
    assert result == "0109521234543213" + GS + "17261231" + GS + "10LOT"


@pytest.mark.unit
def test_query_percent_decode():
    """Valeur pourcent-encodée dans la query (%2F -> /) doit être décodée."""
    result = digital_link_to_gs1_string(
        "https://id.gs1.org/01/09521234543213?10=LOT%2FA"
    )
    assert result == "0109521234543213" + GS + "10LOT/A"


@pytest.mark.unit
def test_path_percent_decode():
    """Valeur pourcent-encodée dans le path (%2F -> /) doit être décodée.

    Note : le module applique déjà unquote sur les valeurs du path (lot B1).
    Ce test peut déjà passer - son résultat réel est rapporté tel quel.
    """
    result = digital_link_to_gs1_string(
        "https://id.gs1.org/01/09521234543213/10/LOT%2FA"
    )
    assert result == "0109521234543213" + GS + "10LOT/A"


@pytest.mark.unit
def test_sans_query_inchange():
    """Non-régression B1 - comportement sans query string inchangé.

    Doit passer dès maintenant (comportement lot B1 préservé).
    """
    result = digital_link_to_gs1_string(
        "https://id.gs1.org/01/09521234543213/21/XYZ"
    )
    assert result == "0109521234543213" + GS + "21XYZ"
