import numpy as np
import matplotlib.pyplot as plt
# Calcule le payoff brut d'un call/put européen à maturité.

def calculer_call_payoff(S_T: float, K: float) -> float :
    call_payoff = max(S_T - K, 0)
    return call_payoff

def calculer_put_payoff(S_T: float, K: float) -> float :
    put_payoff = max(K - S_T, 0)
    return put_payoff

# Calcule le P&L net d'un call/put long à maturité.

def calculer_call_PnL(S_T: float, K: float, C: float) -> float : 
    return calculer_call_payoff(S_T, K) - C

def calculer_put_PnL(S_T: float, K: float, P: float) -> float : 
    return calculer_put_payoff(S_T, K) - P


# Graphiques payoffs bruts et PnL
# Trace les payoffs bruts et les P&L nets d'un call et d'un put en fonction de plusieurs prix possibles du sous-jacent à maturité.

def tracer_payoffs(K: float, C: float, P: float) -> None:

    valeurs_S_T = np.linspace(0.5 * K, 1.5 * K, 200)

    payoffs_call = [
    calculer_call_payoff(prix_courant, K)
    for prix_courant in valeurs_S_T
    ]
    pnl_call = [
    calculer_call_PnL(prix_courant, K, C)
    for prix_courant in valeurs_S_T
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].plot(valeurs_S_T, payoffs_call, label="Payoff brut call")
    axes[0].plot(valeurs_S_T, pnl_call, label="PnL net call")
    axes[0].axvline(x=K, color="grey", linestyle="--", label="Strike")
    axes[0].axvline(x=K+C, color="red", linestyle="--", label="Breakeven call")
    axes[0].axhline(y=0, color="grey", linestyle="--")
    axes[0].set_xlabel("Valeur du sous-jacent à maturité")
    axes[0].set_ylabel("Payoff brut et PnL du call à maturité")
    axes[0].set_title("Payoff et PnL d’un call européen à maturité")
    axes[0].legend()
    axes[0].grid(linestyle="--", alpha=0.3)

    payoffs_put = [
    calculer_put_payoff(prix_courant, K)
    for prix_courant in valeurs_S_T
    ]
    pnl_put = [
    calculer_put_PnL(prix_courant, K, P)
    for prix_courant in valeurs_S_T
    ]

    
    axes[1].plot(valeurs_S_T, payoffs_put, label="Payoff brut put")
    axes[1].plot(valeurs_S_T, pnl_put, label="PnL net put")
    axes[1].axvline(x=K, color="grey", linestyle="--", label="Strike")
    axes[1].axvline(x=K-P, color="red", linestyle="--", label="Breakeven put")
    axes[1].axhline(y=0, color="grey", linestyle="--")
    axes[1].set_xlabel("Valeur du sous-jacent à maturité")
    axes[1].set_ylabel("Payoff brut et PnL du put à maturité")
    axes[1].set_title("Payoff et PnL d’un put européen à maturité")
    axes[1].legend()
    axes[1].grid(linestyle="--", alpha=0.3)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    tracer_payoffs(K=100, C=4, P=3)


