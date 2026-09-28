import pytest
import numpy as np
from monte_carlo.autocall import simuler_trajectoires
from monte_carlo.autocall import autocall

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
