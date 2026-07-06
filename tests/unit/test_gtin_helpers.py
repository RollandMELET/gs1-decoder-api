"""
Tests unitaires - helpers de normalisation GTIN (pad_gtin14, gtin_indicator).

Phase RED : ces tests échouent car les fonctions n'existent pas encore.
Les vecteurs sont des GTIN réels vérifiés avec chiffre de contrôle correct.
"""

import pytest
from app.gs1_parser import pad_gtin14, gtin_indicator, is_valid_gtin


@pytest.mark.unit
class TestPadGtin14:
    """Normalisation d'un GTIN court (8, 12, 13) vers 14 chiffres par zéro-padding.

    RED attendu : les fonctions pad_gtin14 et gtin_indicator n'existent pas.
    """

    @pytest.mark.parametrize(
        "gtin_court,attendu",
        [
            pytest.param(
                "96385074",
                "00000096385074",
                id="gtin8-vers-gtin14",
            ),
            pytest.param(
                "036000291452",
                "00036000291452",
                id="gtin12-vers-gtin14",
            ),
            pytest.param(
                "4006381333931",
                "04006381333931",
                id="gtin13-vers-gtin14",
            ),
            pytest.param(
                "03760423190005",
                "03760423190005",
                id="gtin14-inchange",
            ),
        ],
    )
    def test_pad_gtin14_normalise_correctement(
        self, gtin_court: str, attendu: str
    ) -> None:
        """pad_gtin14 complète par des zéros à gauche jusqu'à 14 chiffres."""
        assert pad_gtin14(gtin_court) == attendu, (
            f"pad_gtin14({gtin_court!r}) devrait retourner {attendu!r}, "
            f"got {pad_gtin14(gtin_court)!r}"
        )

    def test_pad_gtin14_propriete_validite_preservee(self) -> None:
        """Propriété : le padding préserve la validité du chiffre de contrôle GS1.

        Pour chaque GTIN valide (8, 12, 13, 14), is_valid_gtin(pad_gtin14(g)) reste True.
        """
        gtin_valides = [
            "96385074",          # GTIN-8
            "036000291452",      # GTIN-12
            "4006381333931",     # GTIN-13
            "03760423190005",    # GTIN-14
        ]

        for gtin in gtin_valides:
            assert is_valid_gtin(gtin) is True, (
                f"Précondition : {gtin!r} doit être un GTIN valide"
            )
            padded = pad_gtin14(gtin)
            assert is_valid_gtin(padded) is True, (
                f"pad_gtin14({gtin!r}) -> {padded!r} : "
                f"le padding doit préserver la validité du chiffre de contrôle"
            )

    @pytest.mark.parametrize(
        "gtin_invalide,description",
        [
            pytest.param("12345", "5 chiffres (longueur illégale)", id="gtin5"),
            pytest.param("abc", "caractères non numériques", id="non_numerique"),
            pytest.param("", "chaîne vide", id="vide"),
        ],
    )
    def test_pad_gtin14_raise_value_error_sur_entree_invalide(
        self, gtin_invalide: str, description: str
    ) -> None:
        """pad_gtin14 lève ValueError pour les entrées malformées.

        Les longueurs légales sont : 8, 12, 13, 14.
        Les entrées non numériques ou vides lèvent ValueError.
        """
        with pytest.raises(ValueError) as exc_info:
            pad_gtin14(gtin_invalide)
        assert "GTIN" in str(exc_info.value) or "valide" in str(exc_info.value), (
            f"pad_gtin14({gtin_invalide!r}) : message d'erreur doit mentionner GTIN invalide"
        )


@pytest.mark.unit
class TestGtinIndicator:
    """Extraction du chiffre indicateur (1er chiffre du GTIN-14 normalisé)."""

    @pytest.mark.parametrize(
        "gtin,indicateur_attendu",
        [
            pytest.param(
                "03760423190005",
                "0",
                id="gtin14-indicateur-0",
            ),
            pytest.param(
                "96385074",
                "0",
                id="gtin8-pad-puis-indicateur-0",
            ),
            pytest.param(
                "10000000000009",
                "1",
                id="gtin14-indicateur-1",
            ),
        ],
    )
    def test_gtin_indicator_retourne_premier_chiffre_normalise(
        self, gtin: str, indicateur_attendu: str
    ) -> None:
        """gtin_indicator retourne le 1er chiffre du GTIN-14 normalisé (pad_gtin14(gtin)[0])."""
        result = gtin_indicator(gtin)
        assert result == indicateur_attendu, (
            f"gtin_indicator({gtin!r}) devrait retourner {indicateur_attendu!r}, "
            f"got {result!r}"
        )

    def test_gtin_indicator_est_chiffre_unique(self) -> None:
        """L'indicateur doit être une chaîne d'un seul caractère, numérique."""
        gtin = "03760423190005"
        result = gtin_indicator(gtin)
        assert len(result) == 1, (
            f"gtin_indicator doit retourner un seul caractère, got {len(result)}"
        )
        assert result.isdigit(), (
            f"gtin_indicator doit retourner un chiffre, got {result!r}"
        )
