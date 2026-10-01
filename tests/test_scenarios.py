import pytest

from risk.scenarios import stress_spot_call, stress_spot_put, stress_vol_call


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