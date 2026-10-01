import pytest
import numpy as np
from monte_carlo.autocall import (
    simuler_trajectoires, 
    autocall, 
    cashflow_final_actualise, 
    dates_paiement_autocall, 
    valoriser_autocall, 
    analyser_convergence)
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

    assert np.allclose(cashflow_final, [108])

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

    assert np.allclose(cashflow_final, [108])

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