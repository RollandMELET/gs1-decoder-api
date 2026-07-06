"""
Tests unitaires - validation du chiffre de contrôle GS1 mod-10 (is_valid_gtin).

Phase RED : ces tests DOIVENT échouer avec l'implémentation actuelle buggée.
Les branches de parité sont inversées dans gs1_parser.py pour GTIN-12 et GTIN-13.
Les vecteurs sont des GTIN réels vérifiés hors du code testé (pas de tautologie).
"""

import pytest
from app.gs1_parser import is_valid_gtin


@pytest.mark.unit
class TestGtinValide:
    """GTIN avec chiffre de contrôle correct - attendu True.

    RED attendu : les cas GTIN-12 et GTIN-13 échouent car le code
    renvoie False à tort (branches de parité inversées).
    """

    @pytest.mark.parametrize(
        "gtin",
        [
            pytest.param("96385074",         id="gtin8-valide"),
            pytest.param("036000291452",     id="gtin12-valide-upc-a"),
            pytest.param("4006381333931",    id="gtin13-valide-ean13-a"),
            pytest.param("5901234123457",    id="gtin13-valide-ean13-b"),
            pytest.param("03760423190005",   id="gtin14-valide"),
        ],
    )
    def test_gtin_valide_retourne_true(self, gtin: str) -> None:
        assert is_valid_gtin(gtin) is True, (
            f"GTIN valide {gtin!r} devrait retourner True - chiffre de contrôle correct"
        )


@pytest.mark.unit
class TestGtinInvalide:
    """GTIN avec chiffre de contrôle errone - attendu False.

    Ces cas doivent passer en RED (le code detecte bien les GTIN invalides).
    Chaque vecteur est le GTIN valide precedent avec son dernier chiffre incremente.
    """

    @pytest.mark.parametrize(
        "gtin",
        [
            pytest.param("96385075",         id="gtin8-chiffre-controle-faux"),
            pytest.param("036000291453",     id="gtin12-chiffre-controle-faux"),
            pytest.param("4006381333932",    id="gtin13-chiffre-controle-faux"),
            pytest.param("03760423190006",   id="gtin14-chiffre-controle-faux"),
        ],
    )
    def test_gtin_invalide_retourne_false(self, gtin: str) -> None:
        assert is_valid_gtin(gtin) is False, (
            f"GTIN invalide {gtin!r} devrait retourner False - chiffre de controle incorrect"
        )


@pytest.mark.unit
class TestGtinCasDeGarde:
    """Cas limites : entrees malformees ou illicites - attendu False dans tous les cas."""

    def test_chaine_vide_retourne_false(self) -> None:
        assert is_valid_gtin("") is False

    def test_chaine_non_numerique_retourne_false(self) -> None:
        # Chaine avec lettres - ne peut pas etre un GTIN
        assert is_valid_gtin("abc4006381333931") is False

    def test_longueur_illegale_5_chiffres_retourne_false(self) -> None:
        # 5 chiffres : longueur non supportee par GS1 (valides : 8, 12, 13, 14)
        assert is_valid_gtin("12345") is False

    def test_longueur_illegale_10_chiffres_retourne_false(self) -> None:
        # 10 chiffres : longueur non supportee
        assert is_valid_gtin("1234567890") is False

    def test_chaine_avec_espaces_retourne_false(self) -> None:
        # Espaces inclus - non numerique au sens isdigit
        assert is_valid_gtin("036000 291452") is False
