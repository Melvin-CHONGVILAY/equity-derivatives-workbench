import math
import pytest
from pricing.black_scholes import prix_call
from greeks.greeks import delta_call, gamma_call, vega_call, theta_call, rho_call
from risk.pnl_explain import (
    pnl_explain,
    pnl_reel,
    pnl_estime_greeks,
    pnl_couverture_delta,
    balayage_chocs_spot
)

# Option ATM 1 an, même cas que dans les autres fichiers de tests
MARCHE = dict(S=100, K=100, T=1, r=0.02, sigma=0.20, q=0.0)


# --- Aucun choc -------------------------------------------------------------

@pytest.mark.parametrize("type_option", ["call", "put"])
def test_aucun_choc_pnl_nul(type_option):
    resultat = pnl_explain(**MARCHE, type_option=type_option)

    assert resultat["prix_apres"] == pytest.approx(resultat["prix_avant"])
    assert resultat["pnl_reel"] == pytest.approx(0.0, abs=1e-12)
    assert resultat["pnl_estime"] == pytest.approx(0.0, abs=1e-12)
    assert resultat["ecart"] == pytest.approx(0.0, abs=1e-12)

    # Pas de division par un P&L nul
    assert resultat["ecart_pourcentage"] is None
    assert "Aucun choc" in resultat["commentaire"]


# --- Sens du P&L ------------------------------------------------------------

def test_call_choc_spot_positif():
    resultat = pnl_explain(**MARCHE, type_option="call", choc_spot=0.05)

    assert resultat["prix_apres"] > resultat["prix_avant"]
    assert resultat["pnl_reel"] > 0
    assert resultat["pnl_estime"] > 0


def test_call_choc_spot_negatif():
    resultat = pnl_explain(**MARCHE, type_option="call", choc_spot=-0.05)

    assert resultat["prix_apres"] < resultat["prix_avant"]
    assert resultat["pnl_reel"] < 0
    assert resultat["pnl_estime"] < 0


def test_put_choc_spot_positif():
    resultat = pnl_explain(**MARCHE, type_option="put", choc_spot=0.05)

    assert resultat["prix_apres"] < resultat["prix_avant"]
    assert resultat["pnl_reel"] < 0
    assert resultat["pnl_estime"] < 0


def test_put_choc_spot_negatif():
    resultat = pnl_explain(**MARCHE, type_option="put", choc_spot=-0.05)

    assert resultat["pnl_reel"] > 0
    assert resultat["pnl_estime"] > 0


# --- Cohérence interne ------------------------------------------------------

def test_full_repricing_coherent():
    resultat = pnl_reel(
        **MARCHE, type_option="call",
        choc_spot=0.03, choc_vol=0.02, choc_taux=0.001, jours=10
    )

    prix_avant_attendu = prix_call(100, 100, 1, 0.02, 0.20, 0.0)
    prix_apres_attendu = prix_call(103, 100, 1 - 10 / 365, 0.021, 0.22, 0.0)

    assert resultat["prix_avant"] == pytest.approx(prix_avant_attendu)
    assert resultat["prix_apres"] == pytest.approx(prix_apres_attendu)
    assert resultat["pnl_reel"] == pytest.approx(
        resultat["prix_apres"] - resultat["prix_avant"]
    )


def test_pnl_estime_somme_des_contributions():
    resultat = pnl_explain(
        **MARCHE, type_option="put",
        choc_spot=-0.04, choc_vol=0.03, choc_taux=-0.002, jours=7
    )

    somme = sum(resultat["contributions"].values())

    assert resultat["pnl_estime"] == pytest.approx(somme)
    assert resultat["ecart"] == pytest.approx(
        resultat["pnl_reel"] - resultat["pnl_estime"]
    )
    assert set(resultat["contributions"]) == {"delta", "gamma", "theta", "vega", "rho"}


def test_quantite_multiplie_le_pnl():
    unitaire = pnl_explain(**MARCHE, type_option="call", choc_spot=0.02, jours=1)
    # Short de 10 calls : tout est multiplié par -10
    short = pnl_explain(**MARCHE, type_option="call", choc_spot=0.02, jours=1, quantite=-10)

    assert short["pnl_reel"] == pytest.approx(-10 * unitaire["pnl_reel"])
    assert short["pnl_estime"] == pytest.approx(-10 * unitaire["pnl_estime"])
    # Les prix et les Greeks restent ceux d'une option
    assert short["prix_avant"] == pytest.approx(unitaire["prix_avant"])
    assert short["greeks"]["delta"] == pytest.approx(unitaire["greeks"]["delta"])


# --- Contribution de chaque Greek -------------------------------------------

def test_contribution_delta_et_gamma():
    resultat = pnl_estime_greeks(**MARCHE, type_option="call", choc_spot=0.02)

    dS = 100 * 0.02
    delta = delta_call(100, 100, 1, 0.02, 0.20, 0.0)
    gamma = gamma_call(100, 100, 1, 0.02, 0.20, 0.0)

    assert resultat["contributions"]["delta"] == pytest.approx(delta * dS)
    assert resultat["contributions"]["gamma"] == pytest.approx(0.5 * gamma * dS ** 2)
    # Long option = long gamma : la contribution gamma est toujours positive
    assert resultat["contributions"]["gamma"] > 0


@pytest.mark.parametrize("type_option", ["call", "put"])
def test_contribution_vega_unite(type_option):
    # Vega est la dérivée par rapport à sigma (pour 1.00 de vol),
    # donc un choc de 0.01 = 1 point de vol, sans division par 100
    resultat = pnl_explain(**MARCHE, type_option=type_option, choc_vol=0.01)

    vega = vega_call(100, 100, 1, 0.02, 0.20, 0.0)  # même vega call/put
    assert resultat["contributions"]["vega"] == pytest.approx(vega * 0.01)

    # Et cette contribution doit coller au reprix complet (à 1% près)
    assert resultat["contributions"]["vega"] == pytest.approx(resultat["pnl_reel"], rel=1e-2)


@pytest.mark.parametrize("type_option", ["call", "put"])
def test_contribution_rho_unite(type_option):
    # Rho pour 1.00 de taux : un choc de 0.001 = +10 bps
    resultat = pnl_explain(**MARCHE, type_option=type_option, choc_taux=0.001)

    assert resultat["contributions"]["rho"] == pytest.approx(resultat["greeks"]["rho"] * 0.001)
    assert resultat["contributions"]["rho"] == pytest.approx(resultat["pnl_reel"], rel=1e-2)

    if type_option == "call":
        assert resultat["contributions"]["rho"] > 0
    else:
        assert resultat["contributions"]["rho"] < 0


@pytest.mark.parametrize("type_option", ["call", "put"])
def test_contribution_theta_un_jour(type_option):
    # Theta annuel, en temps calendaire (le temps avance -> T diminue)
    # donc 1 jour = theta * 1/365
    resultat = pnl_explain(**MARCHE, type_option=type_option, jours=1)

    assert resultat["contributions"]["theta"] == pytest.approx(
        resultat["greeks"]["theta"] / 365
    )

    # Le passage du temps fait perdre de la valeur à une option ATM achetée
    assert resultat["pnl_reel"] < 0
    assert resultat["contributions"]["theta"] < 0
    assert resultat["contributions"]["theta"] == pytest.approx(resultat["pnl_reel"], rel=1e-2)


def test_theta_maturite_stressee():
    resultat = pnl_reel(**MARCHE, type_option="call", jours=30)

    prix_attendu = prix_call(100, 100, 1 - 30 / 365, 0.02, 0.20, 0.0)
    assert resultat["prix_apres"] == pytest.approx(prix_attendu)


def test_theta_call_formule_existante():
    # Vérifie que le module réutilise bien theta_call de greeks.py
    resultat = pnl_estime_greeks(**MARCHE, type_option="call", jours=1)
    assert resultat["greeks"]["theta"] == pytest.approx(
        theta_call(100, 100, 1, 0.02, 0.20, 0.0)
    )
    assert resultat["greeks"]["rho"] == pytest.approx(
        rho_call(100, 100, 1, 0.02, 0.20, 0.0)
    )


# --- Qualité de l'approximation ---------------------------------------------

@pytest.mark.parametrize("type_option", ["call", "put"])
def test_petit_choc_approximation_proche(type_option):
    # Spot +1%, vol +0.5 pt, 1 jour : le résidu vient des termes d'ordre 3
    # et des effets croisés (vanna, volga), il doit rester sous 2% du P&L réel,
    # ce qui correspond au seuil "écart très faible" du module
    resultat = pnl_explain(
        **MARCHE, type_option=type_option,
        choc_spot=0.01, choc_vol=0.005, jours=1
    )

    assert abs(resultat["ecart"]) < 0.02 * abs(resultat["pnl_reel"])
    assert "faible" in resultat["commentaire"]


@pytest.mark.parametrize("choc_spot", [-0.10, 0.10])
def test_gamma_ameliore_delta_seul(choc_spot):
    # Ajouter le terme gamma (ordre 2) doit rapprocher l'estimation du reprix
    resultat = pnl_explain(**MARCHE, type_option="call", choc_spot=choc_spot)

    erreur_delta_seul = abs(resultat["pnl_reel"] - resultat["contributions"]["delta"])
    erreur_delta_gamma = abs(resultat["ecart"])

    assert erreur_delta_gamma < erreur_delta_seul


def test_gros_choc_reste_coherent():
    # Spot -15%, vol +5 pts, 5 jours : on n'attend pas une égalité,
    # seulement des résultats finis et un résidu non négligeable
    resultat = pnl_explain(
        **MARCHE, type_option="call",
        choc_spot=-0.15, choc_vol=0.05, jours=5
    )

    for cle in ["prix_avant", "prix_apres", "pnl_reel", "pnl_estime", "ecart"]:
        assert math.isfinite(resultat[cle])

    assert resultat["pnl_reel"] < 0
    assert abs(resultat["ecart_pourcentage"]) >= 2
    assert "faible" not in resultat["commentaire"]


# --- Couverture delta -------------------------------------------------------

@pytest.mark.parametrize("choc_spot", [-0.05, 0.05])
def test_couverture_delta_long_gamma_gagne(choc_spot):
    # Call long couvert en delta, sans passage du temps : par convexité du prix,
    # C(S + dS) - C(S) - delta * dS >= 0 quel que soit le sens du mouvement
    resultat = pnl_couverture_delta(**MARCHE, type_option="call", choc_spot=choc_spot)

    assert resultat["pnl_total_couvert"] > 0
    assert resultat["pnl_total_couvert"] < abs(resultat["pnl_option"])
    assert resultat["pnl_total_couvert"] == pytest.approx(
        resultat["pnl_option"] + resultat["pnl_actions"]
    )


def test_couverture_delta_nombre_actions():
    resultat = pnl_couverture_delta(**MARCHE, type_option="call", choc_spot=0.01, quantite=2)

    delta = delta_call(100, 100, 1, 0.02, 0.20, 0.0)
    assert resultat["nb_actions_couverture"] == pytest.approx(-2 * delta)
    assert resultat["pnl_actions"] == pytest.approx(-2 * delta * 1.0)


def test_couverture_delta_estime_proche_reel_petit_choc():
    # Après couverture il reste gamma + theta : petit et bien expliqué
    resultat = pnl_couverture_delta(**MARCHE, type_option="put", choc_spot=0.01, jours=1)

    assert resultat["pnl_estime_couvert"] == pytest.approx(
        resultat["pnl_total_couvert"], abs=1e-3
    )


# --- Balayage ---------------------------------------------------------------

def test_balayage_chocs_spot():
    chocs = [-0.10, -0.02, 0.0, 0.02, 0.10]
    lignes = balayage_chocs_spot(**MARCHE, type_option="call", chocs=chocs)

    assert len(lignes) == len(chocs)
    assert [ligne["choc_spot"] for ligne in lignes] == chocs

    for ligne in lignes:
        # Convexité d'un call long : le reprix est toujours au-dessus du delta seul
        assert ligne["pnl_reel"] >= ligne["pnl_delta_seul"] - 1e-12

    ligne_zero = lignes[2]
    assert ligne_zero["pnl_reel"] == pytest.approx(0.0, abs=1e-12)
    assert ligne_zero["ecart_pourcentage"] is None


# --- Paramètres invalides ---------------------------------------------------

def test_refuse_spot_stresse_nul():
    with pytest.raises(ValueError, match="spot"):
        pnl_explain(**MARCHE, type_option="call", choc_spot=-1.0)


def test_refuse_vol_stressee_nulle():
    with pytest.raises(ValueError, match="volatilité"):
        pnl_explain(**MARCHE, type_option="call", choc_vol=-0.20)


def test_refuse_maturite_depassee():
    with pytest.raises(ValueError, match="maturité"):
        pnl_explain(**MARCHE, type_option="call", jours=365)


def test_refuse_jours_negatifs():
    with pytest.raises(ValueError, match="jours"):
        pnl_explain(**MARCHE, type_option="call", jours=-1)


def test_refuse_type_option_inconnu():
    with pytest.raises(ValueError, match="call"):
        pnl_explain(**MARCHE, type_option="straddle")


def test_refuse_maturite_initiale_nulle():
    parametres = dict(MARCHE)
    parametres["T"] = 0.0
    with pytest.raises(ValueError, match="maturité"):
        pnl_explain(**parametres, type_option="call")
