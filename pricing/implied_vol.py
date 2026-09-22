from greeks.greeks import vega_call
from pricing.black_scholes import prix_call, prix_put


def implied_vol(prix_marche, S, K, T, r, type_option, sigma_initiale=0.20, q=0, tolerance=1e-8, max_iterations=100):
    if type_option == "call":
        fonction_prix = prix_call
    elif type_option == "put":
        fonction_prix = prix_put
    else:
        raise ValueError("type_option doit etre 'call' ou 'put'")
    sigma = sigma_initiale
    for _ in range(max_iterations):
        prix_modele = fonction_prix(S, K, T, r, sigma, q)
        erreur_prix = prix_modele - prix_marche
        if abs(erreur_prix) < tolerance:
            return sigma
        vega = vega_call(S, K, T, r, sigma, q)
        if abs(vega) < 1e-12:
            raise RuntimeError("Vega trop faible : impossible de calculer l'IV")
        sigma = sigma - (erreur_prix / vega)
    raise RuntimeError("Newton-Raphson n'a pas converge")