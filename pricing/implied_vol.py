import math
from greeks.greeks import vega_call
from pricing.black_scholes import prix_call, prix_put


def implied_vol(prix_marche, S, K, T, r, type_option, sigma_initiale=0.20, q=0, tolerance=1e-8, max_iterations=100):
    if type_option == "call":
        fonction_prix = prix_call
        borne_basse = max(S * math.exp(-q * T) - K * math.exp(-r * T), 0)
        borne_haute = S * math.exp(-q * T)
    elif type_option == "put":
        fonction_prix = prix_put
        borne_basse = max(K * math.exp(-r * T) - S * math.exp(-q * T), 0)
        borne_haute = K * math.exp(-r * T)
    else:
        raise ValueError("type_option doit etre 'call' ou 'put'")

    # Hors de ces bornes (arbitrage), aucune volatilité ne redonne le prix.
    # Petite tolérance en bas : un prix Black-Scholes peut tomber sur la borne à l'arrondi près
    if prix_marche < borne_basse - 1e-6 or prix_marche >= borne_haute:
        raise ValueError("Prix hors des bornes de non-arbitrage : pas de vol implicite")

    # Valeur temps quasi nulle (option très ITM ou très OTM) : le prix ne dépend
    # presque plus de la vol, plusieurs sigma redonnent le même prix
    if prix_marche - borne_basse < 1e-6:
        raise ValueError("Valeur temps quasi nulle : la vol implicite n'est pas identifiable")

    sigma = sigma_initiale
    for _ in range(max_iterations):
        prix_modele = fonction_prix(S, K, T, r, sigma, q)
        erreur_prix = prix_modele - prix_marche
        if abs(erreur_prix) < tolerance:
            return sigma
        vega = vega_call(S, K, T, r, sigma, q)
        if abs(vega) < 1e-12:
            raise RuntimeError("Vega trop faible : impossible de calculer l'IV")
        nouvelle_sigma = sigma - (erreur_prix / vega)

        # Garde-fou : quand vega est petit (option très ITM/OTM), le pas de Newton
        # peut envoyer sigma sous 0 ou très loin, on reste alors dans ]0 ; 5]
        if nouvelle_sigma <= 0:
            nouvelle_sigma = sigma / 2
        elif nouvelle_sigma > 5:
            nouvelle_sigma = (sigma + 5) / 2

        sigma = nouvelle_sigma
    raise RuntimeError("Newton-Raphson n'a pas converge")
