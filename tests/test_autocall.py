import pytest
import numpy as np
from monte_carlo.autocall import (
    simuler_trajectoires,
    autocall,
    cashflow_final_actualise,
    dates_paiement_autocall,
    valoriser_autocall,
    analyser_convergence)
from pricing.black_scholes import prix_call
from risk.scenarios import stress_spot_autocall
from scipy.stats import norm
import math

def test_simuler_trajectoires():
    S0=100
    T=1
    r=0.02
    sigma=0.20 
    resultat_trajectoires = simuler_trajectoires(S0, T, r, sigma, q=0.0, n_trajectoires=100, n_pas=12, seed=42)
    assert resultat_trajectoires.shape == (100, 13)
    assert np.allclose(resultat_trajectoires[:, 0], S0)

def test_autocall_rappel_mois_6():
    trajectoires = np.array([
        [100, 98, 96, 95, 97, 99, 103, 105, 102, 101, 99, 98, 97]
    ])

    cashflow_final = autocall(trajectoires)

    assert np.allclose(cashflow_final, [104])

def test_autocall_rappel_mois_3():
    trajectoires = np.array([
        [100, 98, 96, 105, 97, 99, 103, 105, 102, 101, 99, 98, 97]
    ])

    cashflow_final = autocall(trajectoires)

    assert np.allclose(cashflow_final, [102])

def test_autocall_maturite_protege():
    trajectoires = np.array([
        [100, 98, 96, 99, 97, 99, 95, 91, 99, 94, 99, 98, 97]
    ])

    cashflow_final = autocall(trajectoires)

    # Jamais rappelé, 97 >= 60 : capital protégé mais pas de coupon
    assert np.allclose(cashflow_final, [100])

def test_autocall_maturite_perte():
    trajectoires = np.array([
        [100, 98, 96, 99, 97, 99, 95, 91, 86, 70, 62, 59, 55]
    ])

    cashflow_final = autocall(trajectoires)

    assert np.allclose(cashflow_final, [55])

def test_autocall_barriere_protection_egale():
    trajectoires = np.array([
        [100, 98, 96, 99, 97, 99, 95, 91, 86, 70, 62, 59, 60]
    ])

    cashflow_final = autocall(trajectoires)

    assert np.allclose(cashflow_final, [100])

def test_cashflow_actualise():
    cashflow_final = 108
    r = 0.02
    t = 1
    valeur_actuelle = cashflow_final_actualise(cashflow_final, r, t)
    assert np.isclose(valeur_actuelle, cashflow_final*math.exp(-r*t))

def test_paiement_autocall():
    trajectoires = np.array([[100, 98, 96, 105, 97, 99, 95, 91, 86, 70, 62, 59, 60],
                             [100, 98, 96, 99, 97, 99, 105, 91, 86, 70, 62, 59, 60],
                             [100, 98, 96, 99, 97, 99, 91, 91, 86, 105, 62, 59, 60],
                             [100, 98, 96, 99, 97, 99, 95, 91, 86, 70, 62, 59, 60]])
    resultat_date_paiement = dates_paiement_autocall(trajectoires)
    assert np.allclose(resultat_date_paiement, [0.25, 0.5, 0.75, 1.0])

def test_valorisation_autocall_reproductible():
    resultat_1 = valoriser_autocall(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=5000,
        n_pas=12,
        seed=42
    )

    resultat_2 = valoriser_autocall(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=5000,
        n_pas=12,
        seed=42
    )

    assert np.isclose(
        resultat_1["prix"],
        resultat_2["prix"]
    )

    assert np.isclose(
        resultat_1["erreur_standard"],
        resultat_2["erreur_standard"]
    )

def test_probabilites_autocall_comprises_entre_zero_et_un():
    resultat = valoriser_autocall(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=5000,
        n_pas=12,
        seed=42
    )

    cles_probabilites = [
        "probabilite_rappel_anticipe",
        "probabilite_rappel_total",
        "probabilite_rappel_mois_3",
        "probabilite_rappel_mois_6",
        "probabilite_rappel_mois_9",
        "probabilite_rappel_mois_12",
        "probabilite_perte_capital"
    ]

    for cle in cles_probabilites:
        assert 0.0 <= resultat[cle] <= 1.0

def test_coherence_probabilites_rappel():
    resultat = valoriser_autocall(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=5000,
        n_pas=12,
        seed=42
    )

    rappel_anticipe_attendu = (
        resultat["probabilite_rappel_mois_3"]
        + resultat["probabilite_rappel_mois_6"]
        + resultat["probabilite_rappel_mois_9"]
    )

    rappel_total_attendu = (
        rappel_anticipe_attendu
        + resultat["probabilite_rappel_mois_12"]
    )

    assert np.isclose(
        resultat["probabilite_rappel_anticipe"],
        rappel_anticipe_attendu
    )

    assert np.isclose(
        resultat["probabilite_rappel_total"],
        rappel_total_attendu
    )

def test_valorisation_autocall_cas_deterministe():
    resultat = valoriser_autocall(
        S0=100,
        T=1,
        r=0.0,
        sigma=0.0,
        q=0.0,
        n_trajectoires=100,
        n_pas=12,
        seed=42
    )

    assert np.isclose(resultat["prix"], 102.0)
    assert np.isclose(resultat["erreur_standard"], 0.0)

    assert np.isclose(
        resultat["probabilite_rappel_mois_3"],
        1.0
    )

    assert np.isclose(
        resultat["probabilite_rappel_anticipe"],
        1.0
    )

    assert np.isclose(
        resultat["probabilite_perte_capital"],
        0.0
    )

def test_prix_dans_intervalle_confiance():
    resultat = valoriser_autocall(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=5000,
        n_pas=12,
        seed=42
    )

    assert (
        resultat["borne_basse_95"]
        < resultat["prix"]
        < resultat["borne_haute_95"]
    )

    assert resultat["erreur_standard"] > 0.0

def test_convergence_autocall():
    convergence = analyser_convergence(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        nombres_trajectoires=(1000, 10000),
        seed=42
    )

    erreur_1000 = convergence[0]["erreur_standard"]
    erreur_10000 = convergence[1]["erreur_standard"]

    assert erreur_10000 < erreur_1000

CLES_PROBAS = [
    "probabilite_rappel_anticipe",
    "probabilite_rappel_mois_3",
    "probabilite_rappel_mois_6",
    "probabilite_rappel_mois_9",
    "probabilite_rappel_mois_12",
    "probabilite_perte_capital"
]

def test_spot_par_defaut_egal_S0():
    sans_spot = valoriser_autocall(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=5000, seed=42)
    avec_spot = valoriser_autocall(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=5000, seed=42, spot=100)
    assert avec_spot["prix"] == pytest.approx(sans_spot["prix"])
    for cle in CLES_PROBAS:
        assert avec_spot[cle] == pytest.approx(sans_spot[cle])

def test_invariance_echelle_S0():
    # Seuil de rappel, barrière et coupons sont en % de S0 : émettre l'autocall à 80
    # ou à 120 donne les mêmes probabilités, et un prix proportionnel au nominal
    resultat_80 = valoriser_autocall(S0=80, T=1, r=0.02, sigma=0.20, n_trajectoires=5000, seed=42)
    resultat_120 = valoriser_autocall(S0=120, T=1, r=0.02, sigma=0.20, n_trajectoires=5000, seed=42)
    for cle in CLES_PROBAS:
        assert resultat_80[cle] == pytest.approx(resultat_120[cle])
    assert resultat_120["prix"] == pytest.approx(resultat_80["prix"] * 120 / 80)

def test_spot_sous_S0_moins_de_rappel_plus_de_perte():
    # Mêmes tirages (même seed) : seul le spot de départ change
    parametres = dict(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=20000, seed=42)
    bas = valoriser_autocall(**parametres, spot=90)
    initial = valoriser_autocall(**parametres, spot=100)
    haut = valoriser_autocall(**parametres, spot=110)

    assert bas["probabilite_rappel_anticipe"] < initial["probabilite_rappel_anticipe"] < haut["probabilite_rappel_anticipe"]
    assert bas["probabilite_perte_capital"] > initial["probabilite_perte_capital"] > haut["probabilite_perte_capital"]

def test_spot_coherent_avec_stress_spot_autocall():
    # Partir d'un spot à 90 avec S0 = 100 revient au stress "spot -10%" du module scenarios
    direct = valoriser_autocall(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=5000, seed=42, spot=90)
    stress = stress_spot_autocall(S0=100, T=1, r=0.02, sigma=0.20, q=0.0, choc_spot=-0.10, n_trajectoires=5000, seed=42)

    assert direct["prix"] == pytest.approx(stress["prix_apres"])
    assert direct["probabilite_rappel_anticipe"] == pytest.approx(stress["proba_rappel_anticipe_apres"])
    assert direct["probabilite_perte_capital"] == pytest.approx(stress["proba_perte_capital_apres"])

def test_refuse_spot_negatif():
    with pytest.raises(ValueError, match="spot"):
        valoriser_autocall(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=100, spot=0)

def test_autocall_rappel_mois_12_paye_4_coupons():
    # S_T >= S0 à la dernière date : c'est un rappel, les 4 coupons sont payés
    trajectoires = np.array([
        [100, 98, 96, 99, 97, 99, 95, 91, 99, 94, 99, 98, 101]
    ])

    cashflow_final = autocall(trajectoires)

    assert np.allclose(cashflow_final, [108])

def test_prix_autocall_baisse_quand_le_spot_baisse():
    # L'investisseur est implicitement vendeur d'un put à barrière :
    # une baisse du marché après l'émission doit faire baisser le prix
    parametres = dict(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=20000, seed=42)
    bas = valoriser_autocall(**parametres, spot=90)
    initial = valoriser_autocall(**parametres, spot=100)
    haut = valoriser_autocall(**parametres, spot=110)

    assert bas["prix"] < initial["prix"] < haut["prix"]

def test_valeurs_de_reference():
    # Valeurs citées dans le README (S0 = 100, r = 2%, sigma = 20%, 50 000 trajectoires, seed 42)
    resultat = valoriser_autocall(S0=100, T=1, r=0.02, sigma=0.20, n_trajectoires=50000, seed=42)

    assert resultat["prix"] == pytest.approx(100.88, abs=0.01)
    assert resultat["erreur_standard"] == pytest.approx(0.017, abs=0.001)
    assert resultat["probabilite_rappel_anticipe"] == pytest.approx(0.690, abs=0.001)
    assert resultat["probabilite_perte_capital"] == pytest.approx(0.0047, abs=0.0005)

@pytest.mark.parametrize("spot, T", [(90, 1), (100, 1), (110, 1), (100, 2), (95, 0.5)])
def test_proba_premier_rappel_formule_fermee(spot, T):
    # Rappel à la 1re date : P(S(T/4) >= S0) = N(d) avec
    # d = [ln(spot / S0) + (r - q - sigma²/2) * T/4] / (sigma * racine(T/4))
    S0, r, sigma, q, n = 100, 0.02, 0.20, 0.01, 50000
    resultat = valoriser_autocall(S0=S0, T=T, r=r, sigma=sigma, q=q, n_trajectoires=n, seed=7, spot=spot)

    t1 = T / 4
    d = (math.log(spot / S0) + (r - q - sigma**2 / 2) * t1) / (sigma * math.sqrt(t1))
    proba_exacte = norm.cdf(d)
    # Tolérance : 4 erreurs standard d'une proportion estimée sur n tirages
    tolerance = 4 * math.sqrt(proba_exacte * (1 - proba_exacte) / n)

    assert resultat["probabilite_rappel_mois_3"] == pytest.approx(proba_exacte, abs=tolerance)

def test_simulation_retrouve_black_scholes():
    # Le même moteur de simulation, appliqué à un call européen, doit retrouver Black-Scholes
    S0, K, T, r, sigma, q = 100, 105, 1, 0.02, 0.20, 0.01
    trajectoires = simuler_trajectoires(S0, T, r, sigma, q=q, n_trajectoires=200000, seed=1)
    gains = np.maximum(trajectoires[:, -1] - K, 0) * np.exp(-r * T)

    prix_mc = np.mean(gains)
    erreur_standard = np.std(gains, ddof=1) / np.sqrt(len(gains))

    assert abs(prix_mc - prix_call(S0, K, T, r, sigma, q)) < 4 * erreur_standard
    # Forward : E[S_T] = S0 * exp((r - q) * T)
    assert np.mean(trajectoires[:, -1]) == pytest.approx(S0 * math.exp((r - q) * T), rel=0.002)

def test_dates_paiement_suivent_la_maturite():
    trajectoires = np.array([[100, 98, 96, 105, 97, 99, 95, 91, 86, 70, 62, 59, 60],
                             [100, 98, 96, 99, 97, 99, 105, 91, 86, 70, 62, 59, 60],
                             [100, 98, 96, 99, 97, 99, 91, 91, 86, 105, 62, 59, 60],
                             [100, 98, 96, 99, 97, 99, 95, 91, 86, 70, 62, 59, 60]])
    resultat_date_paiement = dates_paiement_autocall(trajectoires, T=2.0)
    assert np.allclose(resultat_date_paiement, [0.5, 1.0, 1.5, 2.0])
