import pytest
import numpy as np
from monte_carlo.autocall import simuler_trajectoires
from monte_carlo.autocall import autocall
from monte_carlo.autocall import cashflow_final_actualise
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

