import pytest
import math
from risk.scenarios import stress_spot_call, stress_spot_put, stress_vol_call, stress_vol_put, stress_vol_autocall, stress_spot_autocall
from risk.scenarios import stress_spot_vol_option, stress_spot_vol_autocall
from monte_carlo.autocall import valoriser_autocall
from pricing.black_scholes import prix_put

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


@pytest.mark.parametrize("choc_spot", [-0.20, -0.05, 0.10])
def test_stress_spot_respecte_la_parite(choc_spot):
    # C - P = S·e^(-qT) - K·e^(-rT) avant et après le choc :
    # variation du call - variation du put = S·e^(-qT)·choc
    S, K, T, r, sigma, q = 100, 95, 0.75, 0.03, 0.25, 0.02
    call = stress_spot_call(S, K, T, r, sigma, q, choc_spot)
    put = stress_spot_put(S, K, T, r, sigma, q, choc_spot)

    attendu = S * math.exp(-q * T) * choc_spot
    assert call["variation_euros"] - put["variation_euros"] == pytest.approx(attendu)


@pytest.mark.parametrize("choc_vol", [-0.05, 0.05, 0.10])
def test_stress_vol_meme_variation_call_et_put(choc_vol):
    # La parité ne dépend pas de la vol : un choc de vol fait varier call et put du même montant
    S, K, T, r, sigma, q = 100, 95, 0.75, 0.03, 0.25, 0.02
    call = stress_vol_call(S, K, T, r, sigma, q, choc_vol)
    put = stress_vol_put(S, K, T, r, sigma, q, choc_vol)

    assert call["variation_euros"] == pytest.approx(put["variation_euros"])


def test_stress_spot_autocall_avec_spot_du_jour():
    # Term sheet à 100, spot du jour à 90 : le prix avant choc est celui de valoriser_autocall
    parametres = dict(S0=100, T=1, r=0.02, sigma=0.20, q=0.0, n_trajectoires=5000, seed=42)
    resultat = stress_spot_autocall(**parametres, choc_spot=-0.10, spot=90)

    avant = valoriser_autocall(**parametres, spot=90)
    apres = valoriser_autocall(**parametres, spot=81)

    assert resultat["prix_avant"] == pytest.approx(avant["prix"])
    assert resultat["prix_apres"] == pytest.approx(apres["prix"])
    assert resultat["proba_rappel_anticipe_avant"] == pytest.approx(avant["probabilite_rappel_anticipe"])
    assert resultat["proba_perte_capital_apres"] == pytest.approx(apres["probabilite_perte_capital"])


def test_stress_vol_autocall_avec_spot_du_jour():
    parametres = dict(S0=100, T=1, r=0.02, q=0.0, n_trajectoires=5000, seed=42, spot=90)
    resultat = stress_vol_autocall(**parametres, sigma=0.20, choc_vol=0.05)

    avant = valoriser_autocall(**parametres, sigma=0.20)
    apres = valoriser_autocall(**parametres, sigma=0.25)

    assert resultat["prix_avant"] == pytest.approx(avant["prix"])
    assert resultat["prix_apres"] == pytest.approx(apres["prix"])
    # Plus de vol = plus de chances de passer sous la barrière
    assert resultat["proba_perte_capital_apres"] > resultat["proba_perte_capital_avant"]


@pytest.mark.parametrize("type_option, stress_spot, stress_vol", [
    ("call", stress_spot_call, stress_vol_call),
    ("put", stress_spot_put, stress_vol_put),
])
def test_stress_spot_vol_option_retrouve_les_stress_simples(type_option, stress_spot, stress_vol):
    S, K, T, r, sigma, q = 100, 95, 0.75, 0.03, 0.25, 0.02

    assert stress_spot_vol_option(S, K, T, r, sigma, q, type_option, -0.10, 0.0) == pytest.approx(stress_spot(S, K, T, r, sigma, q, -0.10))
    assert stress_spot_vol_option(S, K, T, r, sigma, q, type_option, 0.0, 0.05) == pytest.approx(stress_vol(S, K, T, r, sigma, q, 0.05))


def test_stress_spot_vol_option_choc_combine():
    # Krach : spot -15 % et vol +5 pts, reprix complet avec les deux chocs
    resultat = stress_spot_vol_option(100, 100, 1, 0.02, 0.20, 0.0, "put", -0.15, 0.05)

    assert resultat["prix_avant"] == pytest.approx(prix_put(100, 100, 1, 0.02, 0.20, 0.0))
    assert resultat["prix_apres"] == pytest.approx(prix_put(85, 100, 1, 0.02, 0.25, 0.0))


def test_stress_spot_vol_option_refuse_les_entrees_invalides():
    with pytest.raises(ValueError, match="spot stressé"):
        stress_spot_vol_option(100, 100, 1, 0.02, 0.20, 0.0, "call", -1.0, 0.0)
    with pytest.raises(ValueError, match="volatilité stressée"):
        stress_spot_vol_option(100, 100, 1, 0.02, 0.20, 0.0, "call", 0.0, -0.20)
    with pytest.raises(ValueError, match="call"):
        stress_spot_vol_option(100, 100, 1, 0.02, 0.20, 0.0, "autocall", 0.0, 0.0)


def test_stress_spot_vol_autocall_retrouve_les_stress_simples():
    parametres = dict(S0=100, T=1, r=0.02, sigma=0.20, q=0.0, n_trajectoires=5000, seed=42, spot=95)

    assert stress_spot_vol_autocall(**parametres, choc_spot=-0.10, choc_vol=0.0) == pytest.approx(stress_spot_autocall(**parametres, choc_spot=-0.10))
    assert stress_spot_vol_autocall(**parametres, choc_spot=0.0, choc_vol=0.05) == pytest.approx(stress_vol_autocall(**parametres, choc_vol=0.05))


def test_stress_spot_vol_autocall_choc_combine_et_coupon():
    parametres = dict(S0=100, T=1, r=0.02, q=0.0, n_trajectoires=5000, seed=42, coupon=0.03)
    resultat = stress_spot_vol_autocall(**parametres, sigma=0.20, choc_spot=-0.15, choc_vol=0.05)

    apres = valoriser_autocall(**parametres, sigma=0.25, spot=85)
    assert resultat["prix_apres"] == pytest.approx(apres["prix"])
    assert resultat["prix_avant"] == pytest.approx(valoriser_autocall(**parametres, sigma=0.20)["prix"])

    with pytest.raises(ValueError, match="volatilité stressée"):
        stress_spot_vol_autocall(**parametres, sigma=0.20, choc_spot=0.0, choc_vol=-0.20)


def test_stress_autocall_transmet_le_coupon():
    parametres = dict(S0=100, T=1, r=0.02, sigma=0.20, q=0.0, n_trajectoires=5000, seed=42)
    resultat = stress_spot_autocall(**parametres, choc_spot=-0.10, coupon=0.04)

    assert resultat["prix_avant"] == pytest.approx(valoriser_autocall(**parametres, coupon=0.04)["prix"])
    assert stress_vol_autocall(**parametres, choc_vol=0.05, coupon=0.04)["prix_avant"] == pytest.approx(resultat["prix_avant"])
