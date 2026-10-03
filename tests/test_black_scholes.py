import math
import pytest
from pricing.black_scholes import prix_call,prix_put
from pricing.implied_vol import implied_vol

def test_parité_call_put():
    resultat_call = prix_call(100, 100, 1, 0.02, 0.20, q=0)
    resultat_put = prix_put(100, 100, 1, 0.02, 0.20, q=0)
    assert resultat_call-resultat_put == pytest.approx(100-100*math.exp(-0.02*1))

def test_implied_vol_call_retrouve_volatilite_connue():
    volatilite_attendue = 0.20
    prix_marche = prix_call(100, 100, 1, 0.02, volatilite_attendue, q=0)
    volatilite_trouvee = implied_vol(prix_marche, 100, 100, 1, 0.02, type_option="call", sigma_initiale=0.30, q=0)
    assert volatilite_trouvee == pytest.approx(volatilite_attendue)


def test_implied_vol_put_retrouve_volatilite_connue():
    volatilite_attendue = 0.20
    prix_marche = prix_put(100, 100, 1, 0.02, volatilite_attendue, q=0)
    volatilite_trouvee = implied_vol(prix_marche, 100, 100, 1, 0.02,  type_option="put", sigma_initiale=0.30, q=0)
    assert volatilite_trouvee == pytest.approx(volatilite_attendue)

def test_implied_vol_refuse_type_option_invalide():
    with pytest.raises(ValueError, match="type_option"):
        implied_vol(10, 100, 100, 1, 0.02, type_option="straddle")



def test_parite_call_put_avec_dividende():
    S, K, T, r, sigma, q = 100, 95, 0.5, 0.03, 0.25, 0.02
    resultat_call = prix_call(S, K, T, r, sigma, q)
    resultat_put = prix_put(S, K, T, r, sigma, q)
    assert resultat_call-resultat_put == pytest.approx(S*math.exp(-q*T)-K*math.exp(-r*T))

def test_vol_quasi_nulle_donne_valeur_intrinseque_actualisee():
    # Sans vol, le sous-jacent suit le forward : le call vaut S - K*exp(-rT) s'il est ITM
    assert prix_call(110, 100, 1, 0.02, 1e-6, 0) == pytest.approx(110-100*math.exp(-0.02))
    assert prix_call(90, 100, 1, 0.02, 1e-6, 0) == pytest.approx(0.0, abs=1e-10)
    assert prix_put(90, 100, 1, 0.02, 1e-6, 0) == pytest.approx(100*math.exp(-0.02)-90)

def test_maturite_tres_courte_donne_payoff():
    T = 1e-8
    assert prix_call(105, 100, T, 0.02, 0.20, 0) == pytest.approx(5.0)
    assert prix_put(95, 100, T, 0.02, 0.20, 0) == pytest.approx(5.0)
    assert prix_call(95, 100, T, 0.02, 0.20, 0) == pytest.approx(0.0, abs=1e-10)

def test_spot_egal_strike():
    # ATM avec r > 0 : le call vaut plus que le put (parité)
    resultat_call = prix_call(100, 100, 1, 0.02, 0.20, 0)
    resultat_put = prix_put(100, 100, 1, 0.02, 0.20, 0)
    assert resultat_call > resultat_put > 0
    # Approximation classique ATM : C ~ 0.4 * S * sigma * sqrt(T) (à r = 0)
    assert prix_call(100, 100, 1, 0.0, 0.20, 0) == pytest.approx(0.4*100*0.20, rel=1e-2)

def test_prix_dans_les_bornes():
    for K in [60, 100, 140]:
        resultat_call = prix_call(100, K, 1, 0.02, 0.20, 0)
        resultat_put = prix_put(100, K, 1, 0.02, 0.20, 0)
        assert max(100-K*math.exp(-0.02), 0) <= resultat_call <= 100
        assert max(K*math.exp(-0.02)-100, 0) <= resultat_put <= K*math.exp(-0.02)

def test_prix_croissant_avec_la_vol():
    prix = [prix_call(100, 100, 1, 0.02, sigma, 0) for sigma in [0.10, 0.20, 0.30, 0.40]]
    assert prix == sorted(prix)

@pytest.mark.parametrize("parametres", [
    (100, 100, 0, 0.02, 0.20, 0),     # maturité nulle
    (100, 100, 1, 0.02, 0.0, 0),      # vol nulle
    (100, 100, 1, 0.02, -0.10, 0),    # vol négative
    (0, 100, 1, 0.02, 0.20, 0),       # spot nul
])
def test_refuse_parametres_invalides(parametres):
    with pytest.raises(ValueError):
        prix_call(*parametres)

@pytest.mark.parametrize("K, sigma", [(80, 0.10), (100, 0.40), (120, 0.25), (60, 0.80)])
def test_implied_vol_plusieurs_strikes(K, sigma):
    # (60, 0.80) : call très ITM, vega faible au départ -> cas où Newton divergeait
    prix_marche = prix_call(100, K, 1, 0.02, sigma, 0)
    volatilite_trouvee = implied_vol(prix_marche, 100, K, 1, 0.02, type_option="call")
    assert volatilite_trouvee == pytest.approx(sigma, abs=1e-6)

def test_implied_vol_refuse_prix_hors_bornes():
    # Un call ne peut pas valoir plus que le sous-jacent
    with pytest.raises(ValueError, match="bornes"):
        implied_vol(150, 100, 100, 1, 0.02, type_option="call")
    # Ni moins que sa valeur intrinsèque actualisée
    with pytest.raises(ValueError, match="bornes"):
        implied_vol(1, 120, 100, 1, 0.02, type_option="call")
