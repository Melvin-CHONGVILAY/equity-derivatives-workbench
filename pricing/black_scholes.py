import math
from scipy.stats import norm

def calculer_d1_d2(S, K, T, r, sigma, q):
    # Sans ces contrôles : division par zéro si T ou sigma = 0,
    # et prix faux (négatif) sans erreur si sigma < 0
    if S <= 0 or K <= 0:
        raise ValueError("Le spot et le strike doivent être strictement positifs.")
    if T <= 0:
        raise ValueError("La maturité doit être strictement positive.")
    if sigma <= 0:
        raise ValueError("La volatilité doit être strictement positive.")

    d1 = (math.log(S/K)+(r-q+(sigma**2/2))*T)/(sigma*math.sqrt(T))
    d2 = d1-(sigma*math.sqrt(T))
    return d1, d2

# resultat_d1, resultat_d2 = calculer_d1_d2(100, 100, 1, 0.02, 0.20, 0)
# print(resultat_d1)
# print(resultat_d2)

def prix_call(S, K, T, r, sigma, q):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    call = (S*math.exp(-q*T)*norm.cdf(d1))-(K*math.exp(-r*T)*norm.cdf(d2))
    return call

def prix_put(S, K, T, r, sigma, q):
    d1, d2 = calculer_d1_d2(S, K, T, r, sigma, q)
    put = (K*math.exp(-r*T)*norm.cdf(-d2))-(S*math.exp(-q*T)*norm.cdf(-d1))
    return put

if __name__ == "__main__": 
    resultat_call = prix_call(82, 100, 1, 0.02, 0.20, 0)
    resultat_put = prix_put(110, 100, 1, 0.02, 0.20, 0)

    print(resultat_call)
    print(resultat_put)


