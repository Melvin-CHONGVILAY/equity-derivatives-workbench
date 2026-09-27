import pytest
import numpy as np
from monte_carlo.autocall import simuler_trajectoires

def test_simuler_trajectoires():
    S0=100
    T=1
    r=0.02
    sigma=0.20 
    resultat_trajectoires = simuler_trajectoires(S0, T, r, sigma, q=0.0, n_trajectoires=100, n_pas=12, seed=42)
    assert resultat_trajectoires.shape == (100, 13)
    assert np.allclose(resultat_trajectoires[:, 0], S0)