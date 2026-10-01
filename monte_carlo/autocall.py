import numpy as np
import matplotlib.pyplot as plt

def simuler_trajectoires(S0, T, r, sigma, q=0.0, n_trajectoires=100, n_pas=12, seed=42):
    dt = T / n_pas
    rng = np.random.default_rng(seed)
    chocs = rng.normal(loc=0.0, scale=1.0, size=(n_trajectoires, n_pas))
    drift = (r - q - (sigma**2)/2) * dt
    diffusion = sigma * np.sqrt(dt) * chocs

    log_rendements = drift + diffusion
    log_rendements_cumules = np.cumsum(log_rendements, axis=1)

    trajectoires = np.empty((n_trajectoires, n_pas + 1))
    trajectoires[:, 0] = S0
    trajectoires[:, 1:] = S0 * np.exp(log_rendements_cumules)

    return trajectoires

def tracer_trajectoires(trajectoires, T, n_a_tracer=10):
    n_pas = trajectoires.shape[1] - 1
    dates = np.linspace(0, T, n_pas + 1)

    for trajectoire in trajectoires[:n_a_tracer, :]:
        plt.plot(dates, trajectoire)

    plt.xlabel("Temps (années)")
    plt.ylabel("Prix du sous-jacent")
    plt.title("Trajectoires simulées du sous-jacent")
    plt.grid()
    plt.axhline(y=100, color="grey", linestyle="--")
    plt.show()

    tracer_trajectoires(trajectoires, T=1, n_a_tracer=10)

def autocall(trajectoires, S0=100, seuil_rappel=100):
    prix_a_observation = trajectoires[:,[3,6,9,12]]

    condition_rappel = prix_a_observation >= seuil_rappel
    est_rappelle = np.any(condition_rappel, axis=1)

    premier_rappel = np.argmax(condition_rappel, axis=1)
    nombre_coupons = premier_rappel+1
    nombre_coupons_rappel = np.where(est_rappelle, nombre_coupons, 0)

    coupon_trimestriel = 0.02*S0
    remboursement_rappel = S0+coupon_trimestriel*nombre_coupons_rappel
    tableau_rappel_coupon = np.where(est_rappelle, remboursement_rappel, 0)

    prix_final = trajectoires[:, -1]
    condition_protection = prix_final >= 0.6*S0

    arrive_a_maturite = ~est_rappelle
    remboursement_protege = S0 + 4 * coupon_trimestriel
    remboursement_perte = (prix_final / S0) * S0
    remboursement_maturite_brut = np.where(condition_protection, remboursement_protege, remboursement_perte)

    tableau_maturite = np.where(arrive_a_maturite, remboursement_maturite_brut, 0)

    cashflow_final = tableau_rappel_coupon + tableau_maturite
    return cashflow_final

def dates_paiement_autocall(
    trajectoires,
    seuil_rappel=100,
    T=1.0
):
    n_trajectoires = trajectoires.shape[0]

    # Par défaut, le paiement intervient à maturité.
    dates_paiement = np.ones(n_trajectoires) * T

    rappel_mois_3 = trajectoires[:, 3] >= seuil_rappel

    rappel_mois_6 = (
        (trajectoires[:, 3] < seuil_rappel)
        & (trajectoires[:, 6] >= seuil_rappel)
    )

    rappel_mois_9 = (
        (trajectoires[:, 3] < seuil_rappel)
        & (trajectoires[:, 6] < seuil_rappel)
        & (trajectoires[:, 9] >= seuil_rappel)
    )

    dates_paiement[rappel_mois_3] = 0.25 * T
    dates_paiement[rappel_mois_6] = 0.50 * T
    dates_paiement[rappel_mois_9] = 0.75 * T

    return dates_paiement

def cashflow_final_actualise(cashflow_final, r, t):
    resultats_actualise = cashflow_final*math.exp(-r*t)
    return resultats_actualise

def cashflow_final_actualise(cashflow_final, r, t):
    resultats_actualises = cashflow_final * np.exp(-r * t)
    return resultats_actualises


def autocall_actualise(
    trajectoires,
    r,
    S0=100,
    seuil_rappel=100,
    T=1.0
):
    cashflows = autocall(
        trajectoires,
        S0=S0,
        seuil_rappel=seuil_rappel
    )

    dates_paiement = dates_paiement_autocall(
        trajectoires,
        seuil_rappel=seuil_rappel,
        T=T
    )

    resultats_actualises = cashflow_final_actualise(
        cashflows,
        r,
        dates_paiement
    )

    return resultats_actualises

def statistiques_autocall(
    trajectoires,
    S0=100,
    seuil_rappel=100
):
    prix_observation = trajectoires[:, [3, 6, 9, 12]]

    condition_rappel = prix_observation >= seuil_rappel
    est_rappelle = np.any(condition_rappel, axis=1)

    premier_rappel = np.argmax(condition_rappel, axis=1)

    rappel_mois_3 = est_rappelle & (premier_rappel == 0)
    rappel_mois_6 = est_rappelle & (premier_rappel == 1)
    rappel_mois_9 = est_rappelle & (premier_rappel == 2)
    rappel_mois_12 = est_rappelle & (premier_rappel == 3)

    rappel_anticipe = (
        rappel_mois_3
        | rappel_mois_6
        | rappel_mois_9
    )

    prix_final = trajectoires[:, -1]

    perte_capital = (
        (~est_rappelle)
        & (prix_final < 0.60 * S0)
    )

    return {
        "probabilite_rappel_anticipe": float(np.mean(rappel_anticipe)),
        "probabilite_rappel_total": float(np.mean(est_rappelle)),
        "probabilite_rappel_mois_3": float(np.mean(rappel_mois_3)),
        "probabilite_rappel_mois_6": float(np.mean(rappel_mois_6)),
        "probabilite_rappel_mois_9": float(np.mean(rappel_mois_9)),
        "probabilite_rappel_mois_12": float(np.mean(rappel_mois_12)),
        "probabilite_perte_capital": float(np.mean(perte_capital))
    }

def valoriser_autocall(
    S0,
    T,
    r,
    sigma,
    q=0.0,
    n_trajectoires=50000,
    n_pas=12,
    seed=42,
    seuil_rappel=None
):
    if n_pas != 12:
        raise ValueError(
            "L'autocall simplifié utilise 12 pas mensuels."
        )

    if n_trajectoires < 2:
        raise ValueError(
            "Il faut au moins deux trajectoires."
        )

    if seuil_rappel is None:
        seuil_rappel = S0

    trajectoires = simuler_trajectoires(
        S0=S0,
        T=T,
        r=r,
        sigma=sigma,
        q=q,
        n_trajectoires=n_trajectoires,
        n_pas=n_pas,
        seed=seed
    )

    valeurs_actualisees = autocall_actualise(
        trajectoires=trajectoires,
        r=r,
        S0=S0,
        seuil_rappel=seuil_rappel,
        T=T
    )

    prix = float(np.mean(valeurs_actualisees))

    ecart_type = float(
        np.std(valeurs_actualisees, ddof=1)
    )

    erreur_standard = (
        ecart_type / np.sqrt(n_trajectoires)
    )

    marge_95 = 1.96 * erreur_standard

    statistiques = statistiques_autocall(
        trajectoires,
        S0=S0,
        seuil_rappel=seuil_rappel
    )

    resultats = {
        "prix": prix,
        "erreur_standard": float(erreur_standard),
        "borne_basse_95": float(prix - marge_95),
        "borne_haute_95": float(prix + marge_95),
        "n_trajectoires": n_trajectoires
    }

    resultats.update(statistiques)

    return resultats

def analyser_convergence(
    S0,
    T,
    r,
    sigma,
    q=0.0,
    nombres_trajectoires=(1000, 5000, 10000, 50000),
    seed=42
):
    resultats_convergence = []

    for n_trajectoires in nombres_trajectoires:
        estimation = valoriser_autocall(
            S0=S0,
            T=T,
            r=r,
            sigma=sigma,
            q=q,
            n_trajectoires=n_trajectoires,
            n_pas=12,
            seed=seed
        )

        resultats_convergence.append({
            "n_trajectoires": n_trajectoires,
            "prix": estimation["prix"],
            "erreur_standard": estimation["erreur_standard"]
        })

    return resultats_convergence

if __name__ == "__main__":
    estimation = valoriser_autocall(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=50000,
        n_pas=12,
        seed=42
    )

    print("Prix Monte Carlo :", estimation["prix"])
    print("Erreur standard :", estimation["erreur_standard"])
    print(
        "Intervalle à 95 % :",
        estimation["borne_basse_95"],
        estimation["borne_haute_95"]
    )
    print(
        "Probabilité de rappel anticipé :",
        estimation["probabilite_rappel_anticipe"]
    )
    print(
        "Probabilité de perte en capital :",
        estimation["probabilite_perte_capital"]
    )

    convergence = analyser_convergence(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        seed=42
    )

    for resultat in convergence:
        print(resultat)
    

