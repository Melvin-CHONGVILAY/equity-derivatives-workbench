import numpy as np
import math
from scipy.stats import norm
from pricing.black_scholes import calculer_d1_d2, prix_call, prix_put

def delta_call(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return np.exp(-q*T)*norm.cdf(d1)

# resultat_delta_call = delta_call(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_delta_call)

def gamma_call(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return (np.exp(-q*T)*norm.pdf(d1))/(S*sigma*math.sqrt(T))

# resultat_gamma_call = gamma_call(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_gamma_call)

def vega_call(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return S*np.exp(-q*T)*norm.pdf(d1)*math.sqrt(T)

# resultat_vega_call = vega_call(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_vega_call)

def theta_call(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r,sigma, q)
    return ((-S*np.exp(-q*T)*norm.pdf(d1)*sigma)/(2*math.sqrt(T)))-r*K*np.exp(-r*T)*norm.cdf(d2)+q*S*np.exp(-q*T)*norm.cdf(d1)

# resultat_theta_call = theta_call(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_theta_call)

def rho_call(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return K*T*np.exp(-r*T)*norm.cdf(d2)

# resultat_rho_call = rho_call(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_rho_call)

def delta_put(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return np.exp(-q*T)*(norm.cdf(d1)-1)

# resultat_delta_put = delta_put(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_delta_put)

def gamma_put(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return (np.exp(-q*T)*norm.pdf(d1))/(S*sigma*math.sqrt(T))

# resultat_gamma_put = gamma_put(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_gamma_put)

def vega_put(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return S*np.exp(-q*T)*norm.pdf(d1)*math.sqrt(T)

# resultat_vega_put = vega_put(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_vega_put)

def theta_put(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, T, K, r, sigma, q)
    return ((-S*np.exp(-q*T)*norm.pdf(d1)*sigma)/(2*math.sqrt(T)))+r*K*np.exp(-r*T)*norm.cdf(-d2)-q*S*np.exp(-q*T)*norm.cdf(-d1)

# resultat_theta_put = theta_put(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_theta_put)

def rho_put(S, K, T, r, sigma, q=0.0):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    return -K*np.exp(-r*T)*T*norm.cdf(-d2)

# resultat_rho_put = theta_put(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_theta_put)

def delta_call_num(S, K, T, r, sigma, q=0.0, h=0.01):
    prix_initial = prix_call(S, K, T, r, sigma, q)
    prix_choque = prix_call(S+h, K, T, r, sigma, q)
    return (prix_choque-prix_initial)/h

# resultat_delta_ana = delta_call(100, 100, 1, 0.02, 0.20, 0)
# resultat_delta_num = delta_call_num(100, 100, 1, 0.02, 0.20, 0)

# print(resultat_delta_ana)
# print(resultat_delta_num)