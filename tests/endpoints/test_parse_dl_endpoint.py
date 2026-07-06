"""
Tests TDD - Lot B6 - Phase RED
Endpoint POST /parse/ avec une URI GS1 Digital Link.

test 5 (partiellement RED) : le endpoint doit renvoyer 200, les AIs GTIN et SERIAL
doivent être présents, et decoder_info.is_gs1 doit être True.
Actuellement is_gs1=False car is_gs1_data exclut les URLs http/https.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# URI GS1 Digital Link de référence
_DL_URI = "https://id.gs1.org/01/09521234543213/21/XYZ"


def _find_parsed_item(parsed_list, name):
    """Retourne le premier item dont le champ 'name' correspond, ou None."""
    return next((item for item in parsed_list if item.get("name") == name), None)


@pytest.mark.unit
def test_post_parse_digital_link_200():
    """
    POST /parse/ avec une URI Digital Link doit retourner :
    - HTTP 200
    - un item GTIN avec value "09521234543213"
    - un item SERIAL avec value "XYZ"
    - decoder_info.is_gs1 = True
    """
    resp = client.post("/parse/", json={"raw_data": _DL_URI})

    assert resp.status_code == 200, (
        f"status_code attendu 200, obtenu {resp.status_code} - body: {resp.text[:300]}"
    )

    barcodes = resp.json()["barcodes"]
    assert len(barcodes) >= 1, "La réponse doit contenir au moins un barcode"

    barcode = barcodes[0]
    parsed = barcode["parsed"]
    assert isinstance(parsed, list), (
        f"parsed attendu list (mode verbose forcé), obtenu {type(parsed).__name__}"
    )

    gtin_item = _find_parsed_item(parsed, "GTIN")
    assert gtin_item is not None, "L'item GTIN doit être présent dans parsed"
    assert gtin_item["value"] == "09521234543213", (
        f"GTIN value attendu '09521234543213', obtenu {gtin_item['value']!r}"
    )

    serial_item = _find_parsed_item(parsed, "SERIAL")
    assert serial_item is not None, "L'item SERIAL doit être présent dans parsed"
    assert serial_item["value"] == "XYZ", (
        f"SERIAL value attendu 'XYZ', obtenu {serial_item['value']!r}"
    )

    is_gs1 = barcode["decoder_info"]["is_gs1"]
    assert is_gs1 is True, (
        f"decoder_info.is_gs1 attendu True, obtenu {is_gs1!r} "
        f"(RED attendu - sera corrigé en lot B6 GREEN)"
    )
