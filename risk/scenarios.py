from pricing.black_scholes import prix_call, prix_put
from monte_carlo.autocall import valoriser_autocall


def calculer_variation(prix_avant, prix_apres):
    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (variation_euros / prix_avant) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage
    }


def stress_spot_call(S, K, T, r, sigma, q, choc_spot):
    S_stresse = S * (1 + choc_spot)

    if S_stresse <= 0:
        raise ValueError("Le spot stressé doit être strictement positif.")

    prix_avant = prix_call(S, K, T, r, sigma, q)
    prix_apres = prix_call(S_stresse, K, T, r, sigma, q)

    return calculer_variation(prix_avant, prix_apres)


def stress_spot_put(S, K, T, r, sigma, q, choc_spot):
    S_stresse = S * (1 + choc_spot)

    if S_stresse <= 0:
        raise ValueError("Le spot stressé doit être strictement positif.")

    prix_avant = prix_put(S, K, T, r, sigma, q)
    prix_apres = prix_put(S_stresse, K, T, r, sigma, q)

    return calculer_variation(prix_avant, prix_apres)


def stress_vol_call(S, K, T, r, sigma, q, choc_vol):
    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError("La volatilité stressée doit être strictement positive.")

    prix_avant = prix_call(S, K, T, r, sigma, q)
    prix_apres = prix_call(S, K, T, r, sigma_stressee, q)

    return calculer_variation(prix_avant, prix_apres)


def stress_vol_put(S, K, T, r, sigma, q, choc_vol):
    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError("La volatilité stressée doit être strictement positive.")

    prix_avant = prix_put(S, K, T, r, sigma, q)
    prix_apres = prix_put(S, K, T, r, sigma_stressee, q)

    return calculer_variation(prix_avant, prix_apres)


def comparer_autocall(resultat_avant, resultat_apres):
    resultats = calculer_variation(resultat_avant["prix"], resultat_apres["prix"])

    resultats["proba_rappel_anticipe_avant"] = resultat_avant["probabilite_rappel_anticipe"]
    resultats["proba_rappel_anticipe_apres"] = resultat_apres["probabilite_rappel_anticipe"]
    resultats["proba_perte_capital_avant"] = resultat_avant["probabilite_perte_capital"]
    resultats["proba_perte_capital_apres"] = resultat_apres["probabilite_perte_capital"]

    return resultats


# Pour les deux stress de l'autocall : même seed et même n_trajectoires avant et
# après le choc (nombres aléatoires communs), la variation mesure le choc et pas
# le bruit Monte Carlo.
# S0 = niveau initial du term sheet (nominal, seuil de rappel, barrière),
# spot = niveau du sous-jacent aujourd'hui (S0 par défaut).

def stress_vol_autocall(
    S0,
    T,
    r,
    sigma,
    q,
    choc_vol,
    n_trajectoires=50000,
    seed=42,
    spot=None,
    coupon=0.02
):
    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError("La volatilité stressée doit être strictement positive.")

    resultat_avant = valoriser_autocall(
        S0, T, r, sigma, q,
        n_trajectoires=n_trajectoires, seed=seed, spot=spot, coupon=coupon
    )
    resultat_apres = valoriser_autocall(
        S0, T, r, sigma_stressee, q,
        n_trajectoires=n_trajectoires, seed=seed, spot=spot, coupon=coupon
    )

    return comparer_autocall(resultat_avant, resultat_apres)


def stress_spot_autocall(
    S0,
    T,
    r,
    sigma,
    q,
    choc_spot,
    n_trajectoires=50000,
    seed=42,
    spot=None,
    coupon=0.02
):
    if 1 + choc_spot <= 0:
        raise ValueError("Le spot stressé doit être strictement positif.")

    if spot is None:
        spot = S0

    # Le term sheet (S0) ne bouge pas, seul le spot de départ est choqué.
    # Avec la même seed, les trajectoires après choc sont exactement celles
    # d'avant multipliées par (1 + choc_spot) : le GBM est multiplicatif.
    resultat_avant = valoriser_autocall(
        S0, T, r, sigma, q,
        n_trajectoires=n_trajectoires, seed=seed, spot=spot, coupon=coupon
    )
    resultat_apres = valoriser_autocall(
        S0, T, r, sigma, q,
        n_trajectoires=n_trajectoires, seed=seed, spot=spot * (1 + choc_spot), coupon=coupon
    )

    return comparer_autocall(resultat_avant, resultat_apres)


# Scénarios combinés : spot et vol choqués en même temps (ex. krach = spot -15 %, vol +5 pts).
# Avec choc_vol = 0 on retrouve stress_spot_*, avec choc_spot = 0 on retrouve stress_vol_*.

def stress_spot_vol_option(S, K, T, r, sigma, q, type_option, choc_spot, choc_vol):
    if type_option == "call":
        fonction_prix = prix_call
    elif type_option == "put":
        fonction_prix = prix_put
    else:
        raise ValueError("Le type d'option doit être 'call' ou 'put'.")

    S_stresse = S * (1 + choc_spot)
    sigma_stressee = sigma + choc_vol

    if S_stresse <= 0:
        raise ValueError("Le spot stressé doit être strictement positif.")
    if sigma_stressee <= 0:
        raise ValueError("La volatilité stressée doit être strictement positive.")

    prix_avant = fonction_prix(S, K, T, r, sigma, q)
    prix_apres = fonction_prix(S_stresse, K, T, r, sigma_stressee, q)

    return calculer_variation(prix_avant, prix_apres)


def stress_spot_vol_autocall(
    S0,
    T,
    r,
    sigma,
    q,
    choc_spot,
    choc_vol,
    n_trajectoires=50000,
    seed=42,
    spot=None,
    coupon=0.02
):
    if 1 + choc_spot <= 0:
        raise ValueError("Le spot stressé doit être strictement positif.")

    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError("La volatilité stressée doit être strictement positive.")

    if spot is None:
        spot = S0

    resultat_avant = valoriser_autocall(
        S0, T, r, sigma, q,
        n_trajectoires=n_trajectoires, seed=seed, spot=spot, coupon=coupon
    )
    resultat_apres = valoriser_autocall(
        S0, T, r, sigma_stressee, q,
        n_trajectoires=n_trajectoires, seed=seed, spot=spot * (1 + choc_spot), coupon=coupon
    )

    return comparer_autocall(resultat_avant, resultat_apres)
