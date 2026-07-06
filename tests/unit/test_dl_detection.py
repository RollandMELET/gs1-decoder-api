"""
Tests TDD - Lot B6 - Phase RED
Détection des URI GS1 Digital Link dans barcode_detector.

Ces tests vérifient que :
- test 1 (RED) : is_gs1_data reconnaît une URI Digital Link comme GS1
- test 2 (GREEN) : une URL quelconque n'est pas considérée comme GS1
- test 3 (GREEN) : non-régression format concaténé classique
- test 4 (RED) : get_decoder_info donne le format GS1 QR Code (pas DataMatrix)
  et is_gs1=True pour une URI Digital Link
"""
import pytest

from app.barcode_detector import is_gs1_data, get_decoder_info, DecoderType, BarcodeFormat

# URI GS1 Digital Link de référence pour tous les tests de ce module
_DL_URI = "https://id.gs1.org/01/09521234543213/21/XYZ"


@pytest.mark.unit
def test_is_gs1_data_reconnait_digital_link():
    """Une URI GS1 Digital Link doit être reconnue comme donnée GS1."""
    assert is_gs1_data(_DL_URI) is True


@pytest.mark.unit
def test_is_gs1_data_url_non_dl_reste_false():
    """Une URL générique sans paire AI/valeur dans le chemin n'est PAS du GS1."""
    assert is_gs1_data("https://example.com/about") is False


@pytest.mark.unit
def test_is_gs1_data_concatene_inchange():
    """Non-régression : un GTIN concaténé classique doit rester reconnu comme GS1."""
    assert is_gs1_data("0103760423190005") is True


@pytest.mark.unit
def test_get_decoder_info_dl_format_qr():
    """
    get_decoder_info sur une URI Digital Link doit retourner :
    - is_gs1 = True
    - format = BarcodeFormat.GS1_QRCODE.value ("GS1 QR Code"), pas "DataMatrix"
    """
    info = get_decoder_info(_DL_URI, DecoderType.TEXT_INPUT)

    assert info["is_gs1"] is True, (
        f"is_gs1 attendu True, obtenu {info['is_gs1']!r}"
    )
    assert info["format"] == BarcodeFormat.GS1_QRCODE.value, (
        f"format attendu {BarcodeFormat.GS1_QRCODE.value!r}, obtenu {info['format']!r}"
    )
