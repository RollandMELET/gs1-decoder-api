"""
Tests unitaires - GS1 Digital Link parser (lot B1)
Périmètre : chemin (path) uniquement, AI numériques, host-agnostique.
Query string et alias courts (gtin, lot...) sont réservés aux lots suivants.
"""
import pytest
from app.gs1_digital_link import is_digital_link, digital_link_to_gs1_string


# ---------------------------------------------------------------------------
# is_digital_link
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsDigitalLink:
    def test_true_full_uri_with_serial(self):
        """URI complète avec GTIN-14 et numéro de série - doit retourner True."""
        assert is_digital_link("https://id.gs1.org/01/09521234543213/21/XYZ") is True

    def test_true_http_scheme(self):
        """http:// (sans s) est aussi un Digital Link valide."""
        assert is_digital_link("http://id.gs1.org/01/09521234543213") is True

    def test_false_raw_string_not_url(self):
        """Chaîne brute sans schéma HTTP - pas une URL, doit retourner False."""
        assert is_digital_link("0109521234543213") is False

    def test_false_url_without_ai_pair(self):
        """URL valide mais sans paire /AI/valeur dans le chemin - doit retourner False."""
        assert is_digital_link("https://example.com/about") is False

    def test_false_empty_string(self):
        """Chaîne vide - doit retourner False."""
        assert is_digital_link("") is False


# ---------------------------------------------------------------------------
# digital_link_to_gs1_string
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDigitalLinkToGs1String:
    def test_gtin14_with_serial(self):
        """GTIN-14 suivi d'un numéro de série : deux segments séparés par GS (\x1d)."""
        uri = "https://id.gs1.org/01/09521234543213/21/XYZ"
        result = digital_link_to_gs1_string(uri)
        assert result == "0109521234543213\x1d21XYZ"

    def test_gtin13_padded_to_14(self):
        """GTIN-13 doit être paddé à 14 chiffres (préfixe '0'), pas de GS car segment unique."""
        uri = "https://id.gs1.org/01/4006381333931"
        result = digital_link_to_gs1_string(uri)
        assert result == "0104006381333931"

    def test_raises_on_plain_string(self):
        """Chaîne sans schéma HTTP - doit lever ValueError."""
        with pytest.raises(ValueError):
            digital_link_to_gs1_string("pas une url")

    def test_raises_on_url_without_ai(self):
        """URL sans paire AI valide dans le chemin - doit lever ValueError."""
        with pytest.raises(ValueError):
            digital_link_to_gs1_string("https://example.com/about")
