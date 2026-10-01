from pricing.black_scholes import prix_call, prix_put


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