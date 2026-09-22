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



