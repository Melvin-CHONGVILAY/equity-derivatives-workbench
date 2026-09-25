import numpy as np

def simuler_trajectoires(S0, T, r, sigma, q=0.0, n_trajectoires=100, n_pas=12, seed=None):
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
