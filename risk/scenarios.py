import numpy as np
from pricing.black_scholes import prix_call, prix_put
from monte_carlo.autocall import (
    valoriser_autocall,
    simuler_trajectoires,
    autocall_actualise,
    statistiques_autocall
)

def stress_spot_call(S, K, T, r, sigma, q, choc_spot):
    S_stresse = S * (1 + choc_spot)

    if S_stresse <= 0:
        raise ValueError(
            "Le spot stressé doit être strictement positif."
        )

    prix_avant = prix_call(
        S,
        K,
        T,
        r,
        sigma,
        q
    )

    prix_apres = prix_call(
        S_stresse,
        K,
        T,
        r,
        sigma,
        q
    )

    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (
            variation_euros / prix_avant
        ) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage
    }

def stress_spot_put(S, K, T, r, sigma, q, choc_spot):
    S_stresse = S * (1 + choc_spot)

    if S_stresse <= 0:
        raise ValueError(
            "Le spot stressé doit être strictement positif."
        )

    prix_avant = prix_put(
        S,
        K,
        T,
        r,
        sigma,
        q
    )

    prix_apres = prix_put(
        S_stresse,
        K,
        T,
        r,
        sigma,
        q
    )

    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (
            variation_euros / prix_avant
        ) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage
    }

def stress_vol_call(S, K, T, r, sigma, q, choc_vol):
    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError(
            "La volatilité stressée doit être strictement positive."
        )

    prix_avant = prix_call(
        S,
        K,
        T,
        r,
        sigma,
        q
    )

    prix_apres = prix_call(
        S,
        K,
        T,
        r,
        sigma_stressee,
        q
    )

    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (
            variation_euros / prix_avant
        ) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage
    }

def stress_vol_put(S, K, T, r, sigma, q, choc_vol):
    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError(
            "La volatilité stressée doit être strictement positive."
        )

    prix_avant = prix_put(
        S,
        K,
        T,
        r,
        sigma,
        q
    )

    prix_apres = prix_put(
        S,
        K,
        T,
        r,
        sigma_stressee,
        q
    )

    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (
            variation_euros / prix_avant
        ) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage
    }

def stress_vol_autocall(
    S0,
    T,
    r,
    sigma,
    q,
    choc_vol,
    n_trajectoires=50000,
    seed=42
):
    sigma_stressee = sigma + choc_vol

    if sigma_stressee <= 0:
        raise ValueError(
            "La volatilité stressée doit être strictement positive."
        )

    # Même seed et même n_trajectoires : nombres aléatoires communs
    resultat_avant = valoriser_autocall(
        S0=S0,
        T=T,
        r=r,
        sigma=sigma,
        q=q,
        n_trajectoires=n_trajectoires,
        n_pas=12,
        seed=seed
    )

    resultat_apres = valoriser_autocall(
        S0=S0,
        T=T,
        r=r,
        sigma=sigma_stressee,
        q=q,
        n_trajectoires=n_trajectoires,
        n_pas=12,
        seed=seed
    )

    prix_avant = resultat_avant["prix"]
    prix_apres = resultat_apres["prix"]

    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (
            variation_euros / prix_avant
        ) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage,
        "proba_rappel_anticipe_avant": resultat_avant["probabilite_rappel_anticipe"],
        "proba_rappel_anticipe_apres": resultat_apres["probabilite_rappel_anticipe"],
        "proba_perte_capital_avant": resultat_avant["probabilite_perte_capital"],
        "proba_perte_capital_apres": resultat_apres["probabilite_perte_capital"]
    }

def stress_spot_autocall(
    S0,
    T,
    r,
    sigma,
    q,
    choc_spot,
    n_trajectoires=50000,
    seed=42
):
    if 1 + choc_spot <= 0:
        raise ValueError(
            "Le spot stressé doit être strictement positif."
        )

    # Scénario de base : valorisation existante
    resultat_avant = valoriser_autocall(
        S0=S0,
        T=T,
        r=r,
        sigma=sigma,
        q=q,
        n_trajectoires=n_trajectoires,
        n_pas=12,
        seed=seed
    )

    # Mêmes tirages (même seed), donc nombres aléatoires communs
    trajectoires = simuler_trajectoires(
        S0=S0,
        T=T,
        r=r,
        sigma=sigma,
        q=q,
        n_trajectoires=n_trajectoires,
        n_pas=12,
        seed=seed
    )

    # Choc de spot : on décale tout le chemin, mais le term sheet
    # (S0, seuil de rappel, barrière, nominal) reste celui du strike
    trajectoires_stressees = trajectoires * (1 + choc_spot)

    valeurs = autocall_actualise(
        trajectoires_stressees,
        r,
        S0=S0,
        seuil_rappel=S0,
        T=T
    )

    statistiques = statistiques_autocall(
        trajectoires_stressees,
        S0=S0,
        seuil_rappel=S0
    )

    prix_avant = resultat_avant["prix"]
    prix_apres = float(np.mean(valeurs))

    variation_euros = prix_apres - prix_avant

    if prix_avant == 0:
        variation_pourcentage = None
    else:
        variation_pourcentage = (variation_euros / prix_avant) * 100

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "variation_euros": variation_euros,
        "variation_pourcentage": variation_pourcentage,
        "proba_rappel_anticipe_avant": resultat_avant["probabilite_rappel_anticipe"],
        "proba_rappel_anticipe_apres": statistiques["probabilite_rappel_anticipe"],
        "proba_perte_capital_avant": resultat_avant["probabilite_perte_capital"],
        "proba_perte_capital_apres": statistiques["probabilite_perte_capital"]
    }