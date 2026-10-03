import math
import pytest
from greeks.greeks import delta_call_num,delta_put,delta_call,delta_put_num
from greeks.greeks import (gamma_call, gamma_put, vega_call, vega_put,
                           theta_call, theta_put, rho_call, rho_put)
from pricing.black_scholes import prix_call, prix_put

def test_delta_call_num():
    S = 100
    K = 100
    T = 1
    r = 0.02
    sigma = 0.20
    q = 0
    h=0.01
    delta_ana = delta_call(S, K, T, r, sigma, q)
    delta_num = delta_call_num(S, K, T, r, sigma, q, h)
    assert delta_num == pytest.approx(delta_ana, abs=1e-3)

def test_delta_put_num():
    S = 100
    K = 100
    T = 1
    r = 0.02
    sigma = 0.20
    q = 0
    h=0.01
    delta_ana = delta_put(S, K, T, r, sigma, q)
    delta_num = delta_put_num(S, K, T, r, sigma, q, h)
    assert delta_num == pytest.approx(delta_ana, abs=1e-3)

def test_delta_call_positif():
    S = 100
    K = 100
    T = 1
    r = 0.02
    sigma = 0.20
    q = 0
    resultat_delta_call = delta_call(S, K, T, r, sigma, q)
    assert 0<=resultat_delta_call<=1

def test_delta_put_negatif():
    S = 100
    K = 100
    T = 1
    r = 0.02
    sigma = 0.20
    q = 0
    resultat_delta_put = delta_put(S, K, T, r, sigma, q)
    assert 0>=resultat_delta_put>=-1

# Paramètres communs aux tests ci-dessous (avec dividende pour tester q)
S, K, T, r, sigma, q = 100, 100, 1, 0.02, 0.20, 0.01
h = 1e-5

def test_gamma_vega_identiques_call_put():
    assert gamma_call(S, K, T, r, sigma, q) == pytest.approx(gamma_put(S, K, T, r, sigma, q))
    assert vega_call(S, K, T, r, sigma, q) == pytest.approx(vega_put(S, K, T, r, sigma, q))
    assert gamma_call(S, K, T, r, sigma, q) > 0
    assert vega_call(S, K, T, r, sigma, q) > 0

def test_parite_delta():
    # Dérivée de la parité C - P = S*exp(-qT) - K*exp(-rT) par rapport à S
    ecart = delta_call(S, K, T, r, sigma, q) - delta_put(S, K, T, r, sigma, q)
    assert ecart == pytest.approx(math.exp(-q*T))

@pytest.mark.parametrize("prix, vega", [(prix_call, vega_call), (prix_put, vega_put)])
def test_vega_num(prix, vega):
    # Vega pour 1.00 de vol (et pas par point de vol)
    vega_num = (prix(S, K, T, r, sigma+h, q)-prix(S, K, T, r, sigma-h, q))/(2*h)
    assert vega_num == pytest.approx(vega(S, K, T, r, sigma, q), rel=1e-5)

@pytest.mark.parametrize("prix, rho", [(prix_call, rho_call), (prix_put, rho_put)])
def test_rho_num(prix, rho):
    # Rho pour 1.00 de taux (et pas par point de base)
    rho_num = (prix(S, K, T, r+h, sigma, q)-prix(S, K, T, r-h, sigma, q))/(2*h)
    assert rho_num == pytest.approx(rho(S, K, T, r, sigma, q), rel=1e-5)

@pytest.mark.parametrize("prix, theta", [(prix_call, theta_call), (prix_put, theta_put)])
def test_theta_num(prix, theta):
    # Theta annuel en temps calendaire : quand le temps avance, T diminue
    # donc theta = -dV/dT
    theta_num = -(prix(S, K, T+h, r, sigma, q)-prix(S, K, T-h, r, sigma, q))/(2*h)
    assert theta_num == pytest.approx(theta(S, K, T, r, sigma, q), rel=1e-5)

def test_gamma_num():
    gamma_num = (prix_call(S+0.01, K, T, r, sigma, q)-2*prix_call(S, K, T, r, sigma, q)
                 + prix_call(S-0.01, K, T, r, sigma, q))/0.01**2
    assert gamma_num == pytest.approx(gamma_call(S, K, T, r, sigma, q), rel=1e-4)
