import pytest
from pathlib import Path

from pricing.black_scholes import prix_call, prix_put
from monte_carlo.autocall import valoriser_autocall
from risk.scenarios import stress_spot_call
from risk.pnl_explain import pnl_explain, balayage_chocs_spot

# Tests de l'interface : l'app tourne de bout en bout sans exception, et les
# graphiques affichent bien les valeurs calculées par les modules.
# Ignorés si streamlit n'est pas installé dans le venv.
streamlit_testing = pytest.importorskip("streamlit.testing.v1")
from streamlit.dataframe_util import convert_arrow_bytes_to_pandas_df

# Chemin de app.py à la racine du projet (AppTest résout les chemins depuis tests/)
CHEMIN_APP = str(Path(__file__).parent.parent / "app.py")

# Valeurs par défaut de la barre latérale
S, K, T, r, sigma, q = 100.0, 100.0, 1.0, 0.02, 0.20, 0.0


def lancer_app():
    app = streamlit_testing.AppTest.from_file(CHEMIN_APP, default_timeout=120)
    app.run()
    assert not app.exception
    return app


def donnees_graphique(app, colonne):
    # Données envoyées au navigateur : on cherche la table qui contient cette colonne
    for graphique in app.get("vega_lite_chart"):
        for donnees in graphique.proto.datasets:
            table = convert_arrow_bytes_to_pandas_df(donnees.data.data)
            if colonne in table.columns:
                return table
    raise AssertionError(f"Aucun graphique avec la colonne {colonne}")


def valeur_metrique(app, label):
    for metrique in app.metric:
        if metrique.label == label:
            texte = metrique.value.replace("%", "").replace("+", "").strip()
            return float(texte)
    raise AssertionError(f"Métrique introuvable : {label}")


def test_app_se_lance_sans_erreur():
    app = lancer_app()

    # Aucun avertissement affiché (ex. option dépréciée de st.pyplot)
    assert not app.warning
    assert len(app.tabs) == 4
    # Les 5 graphiques sont en Altair (dessinés par le navigateur) et aucun n'est une image
    # matplotlib, qui se déformait parfois quand on changeait les paramètres
    assert len(app.get("vega_lite_chart")) == 5
    assert len(app.get("image")) == 0


def test_app_put_et_gros_choc():
    app = lancer_app()

    app.sidebar.radio[0].set_value("put")
    app.slider[0].set_value(-20.0)   # choc de spot -20%
    app.run()

    assert not app.exception


def test_app_maturite_depassee_affiche_une_erreur():
    # 60 jours écoulés sur une option de maturité 0.1 an : le module refuse,
    # l'app doit afficher le message au lieu de planter
    app = lancer_app()

    app.sidebar.number_input[2].set_value(0.1)
    app.slider[3].set_value(60)
    app.run()

    assert not app.exception
    assert any("maturité" in erreur.value for erreur in app.error)


def test_metriques_pricing():
    app = lancer_app()

    assert valeur_metrique(app, "Prix du call (Black-Scholes)") == pytest.approx(prix_call(S, K, T, r, sigma, q), abs=1e-4)
    # Les deux côtés de la parité call-put affichent la même valeur
    assert valeur_metrique(app, "Parité : C - P") == pytest.approx(valeur_metrique(app, "Parité : S·e^(-qT) - K·e^(-rT)"))
    # Le prix de marché proposé par défaut est le prix Black-Scholes : on retrouve la vol saisie
    assert valeur_metrique(app, "Volatilité implicite") == pytest.approx(20.0)


def test_graphique_payoff_coherent_avec_black_scholes():
    app = lancer_app()
    table = donnees_graphique(app, "Courbe")

    prix = table[table["Courbe"].str.startswith("Prix")]
    payoff = table[table["Courbe"] == "Payoff à maturité"]
    assert len(prix) == len(payoff) == 200

    for spot, valeur in zip(prix["Spot"], prix["Valeur"]):
        assert valeur == pytest.approx(prix_call(spot, K, T, r, sigma, q))
    for spot, valeur in zip(payoff["Spot"], payoff["Valeur"]):
        assert valeur == pytest.approx(max(spot - K, 0))


def test_graphique_payoff_put():
    app = lancer_app()
    app.sidebar.radio[0].set_value("put")
    app.sidebar.number_input[5].set_value(1.0)   # dividende 1%
    app.run()

    table = donnees_graphique(app, "Courbe")
    prix = table[table["Courbe"].str.startswith("Prix")]
    payoff = table[table["Courbe"] == "Payoff à maturité"]

    for spot, valeur in zip(prix["Spot"], prix["Valeur"]):
        assert valeur == pytest.approx(prix_put(spot, K, T, r, sigma, 0.01))
    for spot, valeur in zip(payoff["Spot"], payoff["Valeur"]):
        assert valeur == pytest.approx(max(K - spot, 0))
    assert valeur_metrique(app, "Parité : C - P") == pytest.approx(valeur_metrique(app, "Parité : S·e^(-qT) - K·e^(-rT)"))
    assert valeur_metrique(app, "Volatilité implicite") == pytest.approx(20.0)


def test_graphique_autocall_coherent_avec_metriques():
    app = lancer_app()
    table = donnees_graphique(app, "Date")
    attendu = valoriser_autocall(K, T, r, sigma, q, n_trajectoires=50000, seed=42, spot=S)

    assert list(table["Date"]) == ["3 mois", "6 mois", "9 mois", "12 mois"]
    for m, proba in zip((3, 6, 9, 12), table["Probabilité (%)"]):
        assert proba == pytest.approx(attendu[f"probabilite_rappel_mois_{m}"] * 100)

    # Les 3 premières barres font le rappel anticipé affiché au-dessus
    assert sum(table["Probabilité (%)"][:3]) == pytest.approx(valeur_metrique(app, "Probabilité de rappel anticipé"), abs=0.05)
    assert valeur_metrique(app, "Prix (% du nominal)") == pytest.approx(attendu["prix"] / K * 100, abs=0.005)
    assert valeur_metrique(app, "Probabilité de perte en capital") == pytest.approx(attendu["probabilite_perte_capital"] * 100, abs=0.005)


def test_graphique_autocall_suit_la_maturite():
    app = lancer_app()
    app.sidebar.number_input[2].set_value(2.0)
    app.run()

    table = donnees_graphique(app, "Date")
    attendu = valoriser_autocall(K, 2.0, r, sigma, q, n_trajectoires=50000, seed=42, spot=S)

    # Observations à T/4, T/2, 3T/4 et T
    assert list(table["Date"]) == ["6 mois", "12 mois", "18 mois", "24 mois"]
    for m, proba in zip((3, 6, 9, 12), table["Probabilité (%)"]):
        assert proba == pytest.approx(attendu[f"probabilite_rappel_mois_{m}"] * 100)
    assert valeur_metrique(app, "Prix (% du nominal)") == pytest.approx(attendu["prix"] / K * 100, abs=0.005)


def test_app_proba_rappel_depend_du_spot():
    # Le niveau initial de l'autocall reste K = 100 : baisser le spot du jour doit réduire
    # la probabilité de rappel anticipé, et le graphique doit suivre
    app = lancer_app()
    proba_initiale = valeur_metrique(app, "Probabilité de rappel anticipé")

    app.sidebar.number_input[0].set_value(90.0)
    app.run()

    assert not app.exception
    assert valeur_metrique(app, "Probabilité de rappel anticipé") < proba_initiale - 10

    table = donnees_graphique(app, "Date")
    attendu = valoriser_autocall(K, T, r, sigma, q, n_trajectoires=50000, seed=42, spot=90.0)
    for m, proba in zip((3, 6, 9, 12), table["Probabilité (%)"]):
        assert proba == pytest.approx(attendu[f"probabilite_rappel_mois_{m}"] * 100)


def test_stress_autocall_coherent_avec_onglet_autocall():
    # Même term sheet, même seed et même nombre de trajectoires : le prix "avant choc"
    # du stress est le prix de l'onglet Autocall, y compris quand le spot n'est pas K
    app = lancer_app()
    app.sidebar.number_input[0].set_value(90.0)
    app.select_slider[1].set_value(50000)
    app.run()

    tableau = app.dataframe[3].value
    prix_onglet_autocall = valeur_metrique(app, "Prix (% du nominal)")
    assert tableau["Prix avant (%)"].tolist() == pytest.approx([prix_onglet_autocall] * len(tableau), abs=0.005)

    spot_moins_10 = tableau[tableau["Scénario"] == "spot -10%"].iloc[0]
    attendu = valoriser_autocall(K, T, r, sigma, q, n_trajectoires=50000, seed=42, spot=81.0)
    assert spot_moins_10["Prix après (%)"] == pytest.approx(attendu["prix"] / K * 100, abs=0.005)
    assert spot_moins_10["Rappel après (%)"] == pytest.approx(attendu["probabilite_rappel_anticipe"] * 100, abs=0.05)


def test_graphique_stress_coherent_avec_tableau():
    app = lancer_app()
    table = donnees_graphique(app, "Scénario")
    tableau = app.dataframe[2].value

    assert list(table["Scénario"]) == list(tableau["Scénario"])
    assert table["Variation (€)"].tolist() == pytest.approx(tableau["Variation (€)"].tolist())

    for choc in (-0.20, -0.10, -0.05, 0.05, 0.10, 0.20):
        ligne = table[table["Scénario"] == f"spot {choc * 100:+.0f}%"].iloc[0]
        assert ligne["Variation (€)"] == pytest.approx(stress_spot_call(S, K, T, r, sigma, q, choc)["variation_euros"], abs=1e-4)
        assert ligne["couleur"] == ("#2ca02c" if choc > 0 else "#d62728")


def test_graphique_pnl_explain_coherent_avec_metriques():
    app = lancer_app()
    app.slider[0].set_value(-10.0)   # choc de spot -10%
    app.slider[1].set_value(3.0)     # vol +3 pts
    app.run()

    table = donnees_graphique(app, "Terme")
    attendu = pnl_explain(S, K, T, r, sigma, q, "call", -0.10, 0.03, 0.0, 1, 1)

    termes = table[table["Terme"] != "résidu"]
    residu = table[table["Terme"] == "résidu"]["P&L (€)"].iloc[0]

    assert list(termes["Terme"]) == list(attendu["contributions"].keys())
    assert termes["P&L (€)"].tolist() == pytest.approx(list(attendu["contributions"].values()))
    # Somme des barres des Greeks = P&L estimé, + le résidu = P&L réel
    assert termes["P&L (€)"].sum() == pytest.approx(attendu["pnl_estime"])
    assert termes["P&L (€)"].sum() + residu == pytest.approx(attendu["pnl_reel"])

    assert valeur_metrique(app, "P&L réel (reprix)") == pytest.approx(attendu["pnl_reel"], abs=1e-4)
    assert valeur_metrique(app, "P&L estimé (Greeks)") == pytest.approx(attendu["pnl_estime"], abs=1e-4)
    assert valeur_metrique(app, "Résidu") == pytest.approx(residu, abs=1e-4)


def test_graphique_balayage_coherent_avec_le_module():
    app = lancer_app()
    table = donnees_graphique(app, "Choc de spot (%)")
    reel = table[table["Courbe"] == "P&L réel (reprix)"]

    attendu = balayage_chocs_spot(S, K, T, r, sigma, q, "call", chocs=[-0.30, 0.0, 0.30])
    for ligne in attendu:
        point = reel[(reel["Choc de spot (%)"] - ligne["choc_spot"] * 100).abs() < 1e-9]
        assert point["P&L (€)"].iloc[0] == pytest.approx(ligne["pnl_reel"])

    # Pas de choc, pas de P&L, quelle que soit la courbe
    au_centre = table[table["Choc de spot (%)"].abs() < 1e-9]
    assert au_centre["P&L (€)"].tolist() == pytest.approx([0.0, 0.0, 0.0])
