from pricing.payoff import (calculer_call_payoff, calculer_put_payoff, calculer_call_PnL, calculer_put_PnL)

# Call ITM
def test_call_payoff_itm():
    resultat_call_payoff = calculer_call_payoff(108, 100)
    assert resultat_call_payoff == 8

def test_call_pnl_itm():
    resultat_call_pnl = calculer_call_PnL(108, 100, 4)
    assert resultat_call_pnl == 4

# Call OTM
def test_call_payoff_otm():
    resultat_call_payoff = calculer_call_payoff(95, 100)
    assert resultat_call_payoff == 0

def test_call_pnl_otm():
    resultat_call_pnl = calculer_call_PnL(95, 100, 4)
    assert resultat_call_pnl == -4 

# Call BE
def test_call_payoff_be():
    resultat_call_payoff = calculer_call_payoff(104, 100)
    assert resultat_call_payoff == 4

def test_call_pnl_be():
    resultat_call_pnl = calculer_call_PnL(104, 100, 4)
    assert resultat_call_pnl == 0 

# Call S_T=K
def test_call_payoff_strike():
    resultats_call_payoff = calculer_call_payoff(100, 100)
    assert resultats_call_payoff == 0

def test_call_pnl_strike():
    resultats_call_pnl = calculer_call_PnL(100, 100, 4)
    assert resultats_call_pnl == -4 

# Put ITM
def test_put_payoff_itm():
    resultat_put_payoff = calculer_put_payoff(90, 100)
    assert resultat_put_payoff == 10

def test_put_pnl_itm():
    resultat_put_pnl = calculer_put_PnL(90, 100, 3)
    assert resultat_put_pnl == 7 

# Put OTM
def test_put_payoff_otm():
    resultat_put_payoff = calculer_put_payoff(105, 100)
    assert resultat_put_payoff == 0

def test_put_pnl_otm():
    resultat_put_pnl = calculer_put_PnL(105, 100, 3)
    assert resultat_put_pnl == -3

# Put BE
def test_put_payoff_be():
    resultat_put_payoff = calculer_put_payoff(97, 100)
    assert resultat_put_payoff == 3

def test_put_pnl_be():
    resultat_put_pnl = calculer_put_PnL(97, 100, 3)
    assert resultat_put_pnl == 0 

# Put S_T=K
def test_put_payoff_strike():
    resultats_put_payoff = calculer_put_payoff(100, 100)
    assert resultats_put_payoff == 0

def test_put_pnl_strike():
    resultats_put_pnl = calculer_put_PnL(100, 100, 3)
    assert resultats_put_pnl == -3