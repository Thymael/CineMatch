import pytest

from scripts.verifier_connexion_tmdb import creer_entetes, valider_token


def test_valider_token_present():
    resultat = valider_token("mon_token")

    assert resultat == "mon_token"


def test_valider_token_absent():
    with pytest.raises(ValueError):
        valider_token(None)


def test_valider_token_vide():
    with pytest.raises(ValueError):
        valider_token("   ")


def test_creer_entetes():
    entetes = creer_entetes("mon_token")

    assert entetes["accept"] == "application/json"
    assert entetes["Authorization"] == "Bearer mon_token"