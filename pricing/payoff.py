# Calcule le payoff brut d'un call/put européen à maturité.

#     S_T : prix du sous-jacent à maturité
#     K   : prix d'exercice (strike)

def calculer_call_payoff(S_T:float, K:float) -> float :
    call_payoff = max(S_T - K, 0)
    return call_payoff

def calculer_put_payoff(S_T:float, K:float) -> float :
    put_payoff = max(K - S_T, 0)
    return put_payoff

# Calcule le P&L net d'un call/put long à maturité.

#     S_T : prix du sous-jacent à maturité
#     K   : prix d'exercice du call
#     C   : prime payée pour acheter le call

def calculer_call_PnL(S_T:float, K:float, C:float) -> float : 
    return calculer_call_payoff(S_T, K) - C

def calculer_put_PnL(S_T:float, K:float, P:float) -> float : 
    return calculer_put_payoff(S_T, K) - P

if __name__ == "__main__":
    K = 100.0
    C = 4.0
    S_T = 108.0

    payoff_call = calculer_call_payoff(S_T, K)
    pnl_call = calculer_call_PnL(S_T, K, C)

    print("Exemple call long :")
    print(f"S_T = {S_T}, K = {K}, prime = {C}")
    print(f"Payoff brut du call = {payoff_call}")
    print(f"P&L net du call = {pnl_call}")