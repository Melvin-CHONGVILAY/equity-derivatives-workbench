import math
from scipy.stats import norm

def calculer_d1_d2(S, K, T, r, sigma, q):
    d1 = (math.log(S/K)+(r-q+(sigma**2/2))*T)/(sigma*math.sqrt(T))
    d2 = d1-(sigma*math.sqrt(T))
return d1, d2

resultat_d1, resultat_d2 = calculer_d1_d2(100, 100, 1, 0.02, 0.20, 0)
print(resultat_d1)
print(resultat_d2)


