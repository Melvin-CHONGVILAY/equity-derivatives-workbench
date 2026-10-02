import pytest
import math
from risk.scenarios import stress_spot_call, stress_spot_put, stress_vol_call, stress_vol_put, stress_vol_autocall, stress_spot_autocall

def test_stress_spot_call_choc_nul():
    resultat = stress_spot_call(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_spot=0.0
    )

    assert resultat["prix_apres"] == pytest.approx(
        resultat["prix_avant"]
    )

    assert resultat["variation_euros"] == pytest.approx(0.0)

    assert resultat["variation_pourcentage"] == pytest.approx(0.0)

def test_stress_spot_call_choc_positif():
    resultat = stress_spot_call(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_spot=0.10
    )

    assert resultat["prix_apres"] > resultat["prix_avant"]

    variation_attendue = (
        resultat["prix_apres"] - resultat["prix_avant"]
    )

    assert resultat["variation_euros"] == pytest.approx(
        variation_attendue
    )

    pourcentage_attendu = (
        variation_attendue / resultat["prix_avant"]
    ) * 100

    assert resultat["variation_pourcentage"] == pytest.approx(
        pourcentage_attendu
    )

def test_stress_spot_call_choc_negatif():
    resultat = stress_spot_call(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_spot=-0.10
    )

    assert resultat["prix_apres"] < resultat["prix_avant"]

    variation_attendue = (
        resultat["prix_apres"] - resultat["prix_avant"]
    )

    assert resultat["variation_euros"] == pytest.approx(
        variation_attendue
    )

    pourcentage_attendu = (
        variation_attendue / resultat["prix_avant"]
    ) * 100

    assert resultat["variation_pourcentage"] == pytest.approx(
        pourcentage_attendu
    )
def test_stress_spot_call_refuse_spot_nul():
    with pytest.raises(
        ValueError,
        match="Le spot stressé doit être strictement positif."
    ):
        stress_spot_call(
            S=100,
            K=100,
            T=1,
            r=0.02,
            sigma=0.20,
            q=0.0,
            choc_spot=-1.0
        )

def test_stress_spot_put_choc_nul():
    resultat = stress_spot_put(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_spot=0.0
    )

    assert resultat["prix_apres"] == pytest.approx(
        resultat["prix_avant"]
    )
    assert resultat["variation_euros"] == pytest.approx(0.0)
    assert resultat["variation_pourcentage"] == pytest.approx(0.0)


def test_stress_spot_put_choc_positif():
    resultat = stress_spot_put(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_spot=0.10
    )

    assert resultat["prix_apres"] < resultat["prix_avant"]

    variation_attendue = (
        resultat["prix_apres"] - resultat["prix_avant"]
    )

    assert resultat["variation_euros"] == pytest.approx(
        variation_attendue
    )

    pourcentage_attendu = (
        variation_attendue / resultat["prix_avant"]
    ) * 100

    assert resultat["variation_pourcentage"] == pytest.approx(
        pourcentage_attendu
    )


def test_stress_spot_put_choc_negatif():
    resultat = stress_spot_put(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_spot=-0.10
    )

    assert resultat["prix_apres"] > resultat["prix_avant"]

    variation_attendue = (
        resultat["prix_apres"] - resultat["prix_avant"]
    )

    assert resultat["variation_euros"] == pytest.approx(
        variation_attendue
    )

    pourcentage_attendu = (
        variation_attendue / resultat["prix_avant"]
    ) * 100

    assert resultat["variation_pourcentage"] == pytest.approx(
        pourcentage_attendu
    )


def test_stress_spot_put_refuse_spot_nul():
    with pytest.raises(
        ValueError,
        match="Le spot stressé doit être strictement positif."
    ):
        stress_spot_put(
            S=100,
            K=100,
            T=1,
            r=0.02,
            sigma=0.20,
            q=0.0,
            choc_spot=-1.0
        )

def test_stress_vol_call_choc_nul():
    resultat = stress_vol_call(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_vol=0.0
    )

    assert resultat["prix_apres"] == pytest.approx(
        resultat["prix_avant"]
    )
    assert resultat["variation_euros"] == pytest.approx(0.0)
    assert resultat["variation_pourcentage"] == pytest.approx(0.0)

def test_stress_vol_call_hausse_volatilite():
    resultat = stress_vol_call(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_vol=0.05
    )

    assert resultat["prix_apres"] > resultat["prix_avant"]

    variation_attendue = (
        resultat["prix_apres"] - resultat["prix_avant"]
    )

    assert resultat["variation_euros"] == pytest.approx(
        variation_attendue
    )

    pourcentage_attendu = (
        variation_attendue / resultat["prix_avant"]
    ) * 100

    assert resultat["variation_pourcentage"] == pytest.approx(
        pourcentage_attendu
    )  

def test_stress_vol_call_baisse_volatilite():
    resultat = stress_vol_call(
        S=100,
        K=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        choc_vol=-0.05
    )

    assert resultat["prix_apres"] < resultat["prix_avant"]
    assert resultat["variation_euros"] < 0
    assert resultat["variation_pourcentage"] < 0

def test_stress_vol_call_refuse_volatilite_nulle():
    with pytest.raises(
        ValueError,
        match="La volatilité stressée doit être strictement positive."
    ):
        stress_vol_call(
            S=100,
            K=100,
            T=1,
            r=0.02,
            sigma=0.20,
            q=0.0,
            choc_vol=-0.20
        )

def test_stress_vol_put_choc_nul():
    resultat = stress_vol_put(
        S=100, K=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_vol=0.0
    )

    assert resultat["prix_apres"] == pytest.approx(
        resultat["prix_avant"]
    )
    assert resultat["variation_euros"] == pytest.approx(0.0)
    assert resultat["variation_pourcentage"] == pytest.approx(0.0)


def test_stress_vol_put_hausse_volatilite():
    resultat = stress_vol_put(
        S=100, K=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_vol=0.05
    )

    assert resultat["prix_apres"] > resultat["prix_avant"]

    variation_attendue = (
        resultat["prix_apres"] - resultat["prix_avant"]
    )
    assert resultat["variation_euros"] == pytest.approx(
        variation_attendue
    )

    pourcentage_attendu = (
        variation_attendue / resultat["prix_avant"]
    ) * 100
    assert resultat["variation_pourcentage"] == pytest.approx(
        pourcentage_attendu
    )


def test_stress_vol_put_baisse_volatilite():
    resultat = stress_vol_put(
        S=100, K=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_vol=-0.05
    )

    assert resultat["prix_apres"] < resultat["prix_avant"]
    assert resultat["variation_euros"] < 0
    assert resultat["variation_pourcentage"] < 0


def test_stress_vol_put_refuse_volatilite_nulle():
    with pytest.raises(
        ValueError,
        match="La volatilité stressée doit être strictement positive."
    ):
        stress_vol_put(
            S=100, K=100, T=1, r=0.02, sigma=0.20, q=0.0,
            choc_vol=-0.20
        )

def test_stress_vol_autocall_choc_nul():
    resultat = stress_vol_autocall(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_vol=0.0, n_trajectoires=5000, seed=42
    )

    # Même seed + même sigma : les deux prix sont identiques
    assert resultat["prix_apres"] == pytest.approx(resultat["prix_avant"])
    assert resultat["variation_euros"] == pytest.approx(0.0)


def test_stress_vol_autocall_reproductible():
    parametres = dict(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_vol=0.05, n_trajectoires=5000, seed=42
    )

    resultat_1 = stress_vol_autocall(**parametres)
    resultat_2 = stress_vol_autocall(**parametres)

    assert resultat_1["prix_apres"] == pytest.approx(resultat_2["prix_apres"])
    assert resultat_1["variation_euros"] == pytest.approx(resultat_2["variation_euros"])


def test_stress_vol_autocall_coherence_variations():
    resultat = stress_vol_autocall(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_vol=0.05, n_trajectoires=5000, seed=42
    )

    assert resultat["variation_euros"] == pytest.approx(
        resultat["prix_apres"] - resultat["prix_avant"]
    )
    assert resultat["variation_pourcentage"] == pytest.approx(
        resultat["variation_euros"] / resultat["prix_avant"] * 100
    )

    for cle in ["prix_avant", "prix_apres", "variation_euros"]:
        assert math.isfinite(resultat[cle])

    for cle in [
        "proba_rappel_anticipe_avant", "proba_rappel_anticipe_apres",
        "proba_perte_capital_avant", "proba_perte_capital_apres"
    ]:
        assert 0.0 <= resultat[cle] <= 1.0


def test_stress_vol_autocall_refuse_volatilite_nulle():
    with pytest.raises(
        ValueError,
        match="La volatilité stressée doit être strictement positive."
    ):
        stress_vol_autocall(
            S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
            choc_vol=-0.20, n_trajectoires=5000, seed=42
        )

def test_stress_spot_autocall_choc_nul():
    resultat = stress_spot_autocall(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_spot=0.0, n_trajectoires=5000, seed=42
    )

    assert resultat["prix_apres"] == pytest.approx(resultat["prix_avant"])
    assert resultat["variation_euros"] == pytest.approx(0.0)


def test_stress_spot_autocall_reproductible():
    parametres = dict(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_spot=-0.10, n_trajectoires=5000, seed=42
    )

    resultat_1 = stress_spot_autocall(**parametres)
    resultat_2 = stress_spot_autocall(**parametres)

    assert resultat_1["prix_apres"] == pytest.approx(resultat_2["prix_apres"])


def test_stress_spot_autocall_coherence_et_probabilites():
    resultat = stress_spot_autocall(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_spot=-0.10, n_trajectoires=5000, seed=42
    )

    assert resultat["variation_euros"] == pytest.approx(
        resultat["prix_apres"] - resultat["prix_avant"]
    )
    for cle in [
        "proba_rappel_anticipe_apres", "proba_perte_capital_apres"
    ]:
        assert 0.0 <= resultat[cle] <= 1.0


def test_stress_spot_autocall_baisse_spot_augmente_risque_perte():
    resultat = stress_spot_autocall(
        S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
        choc_spot=-0.20, n_trajectoires=5000, seed=42
    )

    assert resultat["proba_perte_capital_apres"] > resultat["proba_perte_capital_avant"]
    assert resultat["proba_rappel_anticipe_apres"] < resultat["proba_rappel_anticipe_avant"]


def test_stress_spot_autocall_refuse_spot_nul():
    with pytest.raises(
        ValueError,
        match="Le spot stressé doit être strictement positif."
    ):
        stress_spot_autocall(
            S0=100, T=1, r=0.02, sigma=0.20, q=0.0,
            choc_spot=-1.0, n_trajectoires=5000, seed=42
        )