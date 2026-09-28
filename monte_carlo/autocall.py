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

    log_S = np.zeros((n_trajectoires, n_pas + 1))
    log_S[:, 0] = np.log(S0)
    log_S[:, 1:] = np.log(S0) + log_rendements_cumules

    trajectoires = np.exp(log_S)

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
    plt.show()

if __name__ == "__main__":
    trajectoires = simuler_trajectoires(
        S0=100,
        T=1,
        r=0.02,
        sigma=0.20,
        q=0.0,
        n_trajectoires=100,
        n_pas=12,
        seed=None
    )

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

    

