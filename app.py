# app.py
# Interface Streamlit du projet : lancer avec "streamlit run app.py" depuis la racine.
# L'app ne contient pas de formule : elle appelle uniquement les modules du projet.

import numpy as np
import altair as alt
import streamlit as st
import pandas as pd

# Les graphiques de l'app sont faits avec Altair (dessinés par le navigateur) et pas
# avec matplotlib : matplotlib n'est pas thread-safe, et Streamlit relance le script
# à chaque changement de paramètre pendant que l'ancien calcul dessine encore,
# ce qui déformait parfois les images.

from pricing.black_scholes import prix_call, prix_put
from pricing.implied_vol import implied_vol
from monte_carlo.autocall import valoriser_autocall, analyser_convergence
from risk.scenarios import (
    stress_spot_call, stress_spot_put,
    stress_vol_call, stress_vol_put,
    stress_spot_autocall, stress_vol_autocall
)
from risk.pnl_explain import (
    prix_option, greeks_option,
    pnl_explain, pnl_couverture_delta, balayage_chocs_spot
)

st.set_page_config(page_title="Equity Derivatives Workbench", layout="wide")
st.title("Equity Derivatives Pricing & Risk Workbench")
st.caption("Black-Scholes, Greeks, autocall Monte Carlo, stress tests et P&L Explain")


# --- Paramètres de marché ---------------------------------------------------
# Saisie en % pour l'utilisateur, convertie en décimal pour les fonctions

st.sidebar.header("Paramètres de marché")
S = st.sidebar.number_input("Spot S", min_value=1.0, value=100.0, step=1.0)
K = st.sidebar.number_input("Strike K", min_value=1.0, value=100.0, step=1.0)
T = st.sidebar.number_input("Maturité T (années)", min_value=0.05, value=1.0, step=0.25)
r = st.sidebar.number_input("Taux r (%)", value=2.0, step=0.25) / 100
sigma = st.sidebar.number_input("Volatilité σ (%)", min_value=1.0, value=20.0, step=1.0) / 100
q = st.sidebar.number_input("Dividende q (%)", min_value=0.0, value=0.0, step=0.25) / 100
type_option = st.sidebar.radio("Option vanille", ["call", "put"], horizontal=True)


# Le Monte Carlo est long : on garde le résultat en cache tant que les paramètres ne changent pas
@st.cache_data
def autocall_cache(S0, T, r, sigma, q, n_trajectoires, seed, spot):
    return valoriser_autocall(S0, T, r, sigma, q, n_trajectoires=n_trajectoires, seed=seed, spot=spot)


@st.cache_data
def convergence_cache(S0, T, r, sigma, q, seed, spot):
    return analyser_convergence(S0, T, r, sigma, q, seed=seed, spot=spot)


@st.cache_data
def stress_autocall_cache(S0, T, r, sigma, q, n_trajectoires, seed, spot, chocs_spot, chocs_vol):
    lignes = []
    for choc in chocs_spot:
        res = stress_spot_autocall(S0, T, r, sigma, q, choc, n_trajectoires, seed, spot=spot)
        lignes.append({"scénario": f"spot {choc * 100:+.0f}%", **res})
    for choc in chocs_vol:
        res = stress_vol_autocall(S0, T, r, sigma, q, choc, n_trajectoires, seed, spot=spot)
        lignes.append({"scénario": f"vol {choc * 100:+.0f} pts", **res})
    return lignes


onglet_pricing, onglet_autocall, onglet_scenarios, onglet_pnl = st.tabs([
    "Pricing & Greeks", "Autocall Monte Carlo", "Scénarios de marché", "Hedge & P&L Explain"
])


# --- Onglet 1 : Pricing & Greeks --------------------------------------------

with onglet_pricing:
    prix = prix_option(S, K, T, r, sigma, q, type_option)
    greeks = greeks_option(S, K, T, r, sigma, q, type_option)

    # Parité call-put : les deux colonnes de droite doivent être égales
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Prix du {type_option} (Black-Scholes)", f"{prix:.4f}")
    col2.metric("Parité : C - P", f"{prix_call(S, K, T, r, sigma, q) - prix_put(S, K, T, r, sigma, q):.4f}")
    col3.metric("Parité : S·e^(-qT) - K·e^(-rT)", f"{S * np.exp(-q * T) - K * np.exp(-r * T):.4f}")

    # Les Greeks du projet sont des dérivées "brutes" (pour 1.00 de vol, 1 an, 1.00 de taux).
    # La colonne de droite les traduit dans les unités utilisées sur un desk.
    st.subheader("Greeks")
    st.dataframe([
        {"Greek": "Delta", "Valeur (module)": greeks["delta"], "Lecture desk": greeks["delta"], "Unité desk": "par 1 € de spot"},
        {"Greek": "Gamma", "Valeur (module)": greeks["gamma"], "Lecture desk": greeks["gamma"], "Unité desk": "variation du delta par 1 € de spot"},
        {"Greek": "Vega", "Valeur (module)": greeks["vega"], "Lecture desk": greeks["vega"] / 100, "Unité desk": "par point de vol"},
        {"Greek": "Theta", "Valeur (module)": greeks["theta"], "Lecture desk": greeks["theta"] / 365, "Unité desk": "par jour calendaire"},
        {"Greek": "Rho", "Valeur (module)": greeks["rho"], "Lecture desk": greeks["rho"] / 100, "Unité desk": "par point de taux (1%)"},
    ], hide_index=True, width="stretch")

    st.subheader("Prix aujourd'hui et payoff à maturité")
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    prix_spots = [prix_option(s, K, T, r, sigma, q, type_option) for s in spots]
    if type_option == "call":
        payoff = np.maximum(spots - K, 0)
    else:
        payoff = np.maximum(K - spots, 0)

    # Ce graphique est dessiné par le navigateur (Altair, installé avec Streamlit) et pas
    # par matplotlib : ce n'est plus une image, donc rien à redimensionner quand on change
    # les valeurs, et on peut lire les points au survol de la souris.
    nom_prix = f"Prix aujourd'hui (T = {T:g} an{'s' if T >= 2 else ''})"
    points = []
    for s, p, v in zip(spots, prix_spots, payoff):
        points.append({"Spot": float(s), "Valeur": float(p), "Courbe": nom_prix})
        points.append({"Spot": float(s), "Valeur": float(v), "Courbe": "Payoff à maturité"})

    # Axes fixés par rapport au strike, avec une petite marge sous 0
    # pour bien voir les courbes qui sont à y = 0
    haut = max(0.6 * K, max(prix_spots) * 1.05)
    echelle_x = alt.Scale(domain=[0.5 * K, 1.5 * K])
    echelle_y = alt.Scale(domain=[-0.05 * haut, haut])

    courbes = alt.Chart(pd.DataFrame(points)).mark_line(clip=True).encode(
        x=alt.X("Spot:Q", scale=echelle_x),
        y=alt.Y("Valeur:Q", scale=echelle_y, title="Valeur de l'option"),
        color=alt.Color("Courbe:N", title=None,
                        scale=alt.Scale(domain=[nom_prix, "Payoff à maturité"], range=["#1f77b4", "#ff7f0e"]),
                        legend=alt.Legend(orient="top-left" if type_option == "call" else "top-right", labelLimit=0)),
        strokeDash=alt.StrokeDash("Courbe:N", legend=None,
                                  scale=alt.Scale(domain=[nom_prix, "Payoff à maturité"], range=[[1, 0], [6, 4]])),
        tooltip=["Courbe:N", alt.Tooltip("Spot:Q", format=".2f"), alt.Tooltip("Valeur:Q", format=".4f")],
    )

    # Repères verticaux : strike (gris) et spot actuel (rouge) s'il est dans la zone affichée
    reperes = [{"Spot": K, "Repère": "Strike", "couleur": "grey", "hauteur_texte": 12}]
    if 0.5 * K <= S <= 1.5 * K:
        reperes.append({"Spot": S, "Repère": "Spot actuel", "couleur": "red", "hauteur_texte": 28})
    base_reperes = alt.Chart(pd.DataFrame(reperes)).encode(
        x=alt.X("Spot:Q", scale=echelle_x),
        color=alt.Color("couleur:N", scale=None),
    )
    lignes_verticales = base_reperes.mark_rule(strokeDash=[3, 3])
    # hauteur_texte en pixels (scale=None) : les deux étiquettes ne se chevauchent pas si S = K
    textes = base_reperes.mark_text(align="left", dx=4).encode(
        text="Repère:N", y=alt.Y("hauteur_texte:Q", scale=None)
    )

    zero = alt.Chart(pd.DataFrame([{"y": 0}])).mark_rule(color="grey", opacity=0.5).encode(y="y:Q")

    graphique = (courbes + lignes_verticales + textes + zero).properties(height=350)
    # Largeur fixe : même taille sur un petit ou un grand écran
    st.altair_chart(graphique, width=700)

    if not 0.5 * K <= S <= 1.5 * K:
        st.caption("Le spot actuel est hors de la zone affichée (50% à 150% du strike).")

    st.subheader("Volatilité implicite")
    st.write("Le marché cote les options en vol : on retrouve σ à partir d'un prix observé (Newton-Raphson).")
    prix_marche = st.number_input("Prix de marché observé", min_value=0.0, value=float(prix), step=0.1, format="%.4f")
    try:
        vol_implicite = implied_vol(prix_marche, S, K, T, r, type_option, q=q)
        st.metric("Volatilité implicite", f"{vol_implicite * 100:.2f} %")
    except ValueError as erreur:
        # Prix saisi impossible ou sans valeur temps : on prévient sans bloquer l'app
        st.warning(str(erreur))
    except RuntimeError as erreur:
        st.error(str(erreur))


# --- Onglet 2 : Autocall Monte Carlo ----------------------------------------

with onglet_autocall:
    # 4 dates d'observation : T/4, T/2, 3T/4 et T (colonnes 3, 6, 9 et 12 des trajectoires)
    dates = [f"{round(T * 3 * k, 2):g} mois" for k in (1, 2, 3, 4)]
    st.write(
        f"Autocall simplifié de maturité {T:g} an{'s' if T >= 2 else ''}, nominal = niveau initial. "
        f"Observations à {', '.join(dates)} : rappel si le sous-jacent est ≥ 100% du niveau initial, "
        "avec un coupon de 2% du nominal par date d'observation écoulée. Sans rappel, le nominal est "
        "remboursé si S_T ≥ 60% du niveau initial, sinon l'investisseur subit la baisse du sous-jacent. "
        "Le prix est la moyenne des cash-flows actualisés sur les trajectoires simulées."
    )
    col1, col2 = st.columns(2)
    n_trajectoires = col1.select_slider(
        "Nombre de trajectoires", options=[1000, 5000, 10000, 50000, 100000], value=50000
    )
    seed = col2.number_input("Seed", min_value=0, value=42, step=1)

    # Le strike K de la barre latérale sert de niveau initial S0 de l'autocall (fixé à l'émission) :
    # seuil de rappel (100 %) et barrière (60 %) sont en % de K. Le spot S est le niveau du jour,
    # point de départ des trajectoires. C'est le rapport S / K qui fait bouger les probabilités.
    st.caption(
        f"Niveau initial de l'autocall = strike K = {K:g}. Spot du jour = {S:g}, soit {S / K * 100:.1f} % du niveau initial."
    )
    resultat = autocall_cache(K, T, r, sigma, q, n_trajectoires, seed, S)

    # Le module travaille en € pour un nominal = K : on affiche tout en % du nominal
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix (% du nominal)", f"{resultat['prix'] / K * 100:.2f} %",
                help=f"Valeur aujourd'hui de l'autocall pour un nominal de {K:g} € : {resultat['prix']:.2f} €")
    col2.metric("Erreur standard", f"{resultat['erreur_standard'] / K * 100:.3f} %")
    col3.metric("IC 95%", f"{resultat['borne_basse_95'] / K * 100:.2f} – {resultat['borne_haute_95'] / K * 100:.2f} %")

    col1, col2 = st.columns(2)
    col1.metric("Probabilité de rappel anticipé", f"{resultat['probabilite_rappel_anticipe'] * 100:.1f} %",
                help="Rappel à l'une des 3 premières dates (le rappel à la dernière date n'est pas anticipé)")
    col2.metric("Probabilité de perte en capital", f"{resultat['probabilite_perte_capital'] * 100:.2f} %")

    probas = [resultat[f"probabilite_rappel_mois_{m}"] for m in (3, 6, 9, 12)]
    barres = [{"Date": d, "Probabilité (%)": p * 100} for d, p in zip(dates, probas)]
    graphique = alt.Chart(pd.DataFrame(barres)).mark_bar().encode(
        x=alt.X("Date:N", sort=dates, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Probabilité (%):Q", scale=alt.Scale(domain=[0, 100])),
        tooltip=["Date:N", alt.Tooltip("Probabilité (%):Q", format=".2f")],
    ).properties(title="Probabilité de rappel à chaque date d'observation", height=300)
    st.altair_chart(graphique, width=700)

    st.subheader("Convergence")
    st.write("L'erreur standard diminue en 1/√N : 4 fois plus de trajectoires divisent l'erreur par 2.")
    convergence = pd.DataFrame([
        {
            "Trajectoires": ligne["n_trajectoires"],
            "Prix (% du nominal)": round(ligne["prix"] / K * 100, 3),
            "Erreur standard (% du nominal)": round(ligne["erreur_standard"] / K * 100, 4),
        }
        for ligne in convergence_cache(K, T, r, sigma, q, seed, S)
    ])
    st.dataframe(convergence, hide_index=True, width="stretch")


# --- Onglet 3 : Scénarios de marché -----------------------------------------

with onglet_scenarios:
    st.subheader(f"Stress test du {type_option} (full repricing)")
    if type_option == "call":
        fonction_spot, fonction_vol = stress_spot_call, stress_vol_call
    else:
        fonction_spot, fonction_vol = stress_spot_put, stress_vol_put

    chocs_spot = [-0.20, -0.10, -0.05, 0.05, 0.10, 0.20]
    chocs_vol = [-0.05, 0.05, 0.10]

    lignes = []
    for choc in chocs_spot:
        lignes.append({"scénario": f"spot {choc * 100:+.0f}%", **fonction_spot(S, K, T, r, sigma, q, choc)})
    for choc in chocs_vol:
        if sigma + choc > 0:
            lignes.append({"scénario": f"vol {choc * 100:+.0f} pts", **fonction_vol(S, K, T, r, sigma, q, choc)})

    tableau = pd.DataFrame([
        {
            "Scénario": ligne["scénario"],
            "Prix avant": round(ligne["prix_avant"], 4),
            "Prix après": round(ligne["prix_apres"], 4),
            "Variation (€)": round(ligne["variation_euros"], 4),
            "Variation (%)": None if ligne["variation_pourcentage"] is None else round(ligne["variation_pourcentage"], 2),
        }
        for ligne in lignes
    ])
    st.dataframe(tableau, hide_index=True, width="stretch")

    # Le graphique reprend exactement le tableau : vert si l'option gagne, rouge si elle perd
    tableau["couleur"] = np.where(tableau["Variation (€)"] >= 0, "#2ca02c", "#d62728")
    graphique = alt.Chart(tableau).mark_bar().encode(
        x=alt.X("Scénario:N", sort=list(tableau["Scénario"]), title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Variation (€):Q", title="Variation (€)"),
        color=alt.Color("couleur:N", scale=None),
        tooltip=["Scénario:N", alt.Tooltip("Variation (€):Q", format="+.4f"), alt.Tooltip("Variation (%):Q", format="+.2f")],
    )
    zero = alt.Chart(pd.DataFrame([{"y": 0}])).mark_rule(color="grey").encode(y="y:Q")
    graphique = (graphique + zero).properties(title=f"Variation du prix du {type_option} par scénario", height=300)
    st.altair_chart(graphique, width=700)

    st.subheader("Stress test de l'autocall")
    st.write(
        f"Même term sheet que l'onglet Autocall (niveau initial = K = {K:g}, spot du jour = {S:g}) et même seed. "
        "Les trajectoires sont les mêmes avant et après le choc : la variation mesure le choc et pas le bruit Monte Carlo."
    )
    n_stress = st.select_slider("Trajectoires pour le stress", options=[5000, 20000, 50000], value=20000)
    chocs_vol_autocall = tuple(c for c in (-0.05, 0.05, 0.10) if sigma + c > 0)
    lignes_autocall = stress_autocall_cache(K, T, r, sigma, q, n_stress, seed, S, (-0.20, -0.10, 0.10), chocs_vol_autocall)

    tableau_autocall = pd.DataFrame([
        {
            "Scénario": ligne["scénario"],
            "Prix avant (%)": round(ligne["prix_avant"] / K * 100, 2),
            "Prix après (%)": round(ligne["prix_apres"] / K * 100, 2),
            "Variation (pts)": round(ligne["variation_euros"] / K * 100, 2),
            "Rappel avant (%)": round(ligne["proba_rappel_anticipe_avant"] * 100, 1),
            "Rappel après (%)": round(ligne["proba_rappel_anticipe_apres"] * 100, 1),
            "Perte avant (%)": round(ligne["proba_perte_capital_avant"] * 100, 2),
            "Perte après (%)": round(ligne["proba_perte_capital_apres"] * 100, 2),
        }
        for ligne in lignes_autocall
    ])
    st.dataframe(tableau_autocall, hide_index=True, width="stretch")
    st.caption("Prix et variation en % du nominal. Rappel = probabilité de rappel anticipé, perte = probabilité de perte en capital.")


# --- Onglet 4 : Hedge & P&L Explain -----------------------------------------

with onglet_pnl:
    st.write(
        "P&L réel = reprix complet avant / après le mouvement. "
        "P&L estimé = Δ·ΔS + ½·Γ·ΔS² + Θ·Δt + Vega·Δσ + ρ·Δr avec les Greeks du point de départ."
    )
    col1, col2, col3 = st.columns(3)
    choc_spot = col1.slider("Choc de spot (%)", -30.0, 30.0, 1.0, 0.5) / 100
    choc_vol = col2.slider("Choc de vol (points)", -10.0, 10.0, 0.5, 0.5) / 100
    choc_taux = col3.slider("Choc de taux (bps)", -100, 100, 0, 5) / 10000
    col1, col2 = st.columns(2)
    jours = col1.slider("Jours écoulés", 0, 60, 1)
    quantite = col2.number_input("Quantité (négatif = short)", value=1, step=1)

    try:
        resultat = pnl_explain(
            S, K, T, r, sigma, q, type_option,
            choc_spot, choc_vol, choc_taux, jours, quantite
        )
    except ValueError as erreur:
        st.error(str(erreur))
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("P&L réel (reprix)", f"{resultat['pnl_reel']:+.4f}")
    col2.metric("P&L estimé (Greeks)", f"{resultat['pnl_estime']:+.4f}")
    if resultat["ecart_pourcentage"] is None:
        col3.metric("Résidu", f"{resultat['ecart']:+.4f}")
    else:
        col3.metric("Résidu", f"{resultat['ecart']:+.4f}", f"{resultat['ecart_pourcentage']:+.2f} % du réel", delta_color="off")

    st.info(resultat["commentaire"])

    noms = list(resultat["contributions"].keys()) + ["résidu"]
    valeurs = list(resultat["contributions"].values()) + [resultat["ecart"]]
    barres = []
    for nom, valeur in zip(noms, valeurs):
        couleur = "#d62728" if nom == "résidu" else "#1f77b4"
        barres.append({"Terme": nom, "P&L (€)": valeur, "couleur": couleur})
    graphique = alt.Chart(pd.DataFrame(barres)).mark_bar().encode(
        x=alt.X("Terme:N", sort=noms, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("P&L (€):Q", title="P&L (€)"),
        color=alt.Color("couleur:N", scale=None),
        tooltip=["Terme:N", alt.Tooltip("P&L (€):Q", format="+.4f")],
    )
    zero = alt.Chart(pd.DataFrame([{"y": 0}])).mark_rule(color="grey").encode(y="y:Q")
    graphique = (graphique + zero).properties(title="Décomposition du P&L par Greek", height=300)
    st.altair_chart(graphique, width=700)

    st.subheader("Couverture en delta")
    couverture = pnl_couverture_delta(
        S, K, T, r, sigma, q, type_option,
        choc_spot, choc_vol, choc_taux, jours, quantite
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Actions en couverture", f"{couverture['nb_actions_couverture']:+.4f}")
    col2.metric("P&L option + actions", f"{couverture['pnl_total_couvert']:+.4f}")
    col3.metric("P&L estimé couvert (Γ + Θ + Vega + ρ)", f"{couverture['pnl_estime_couvert']:+.4f}")

    st.subheader("P&L réel vs estimé selon la taille du choc de spot")
    st.caption(
        "Ici seul le spot bouge (vol, taux et temps inchangés) : l'écart entre le reprix et "
        "delta + gamma grandit avec la taille du choc."
    )
    lignes = balayage_chocs_spot(
        S, K, T, r, sigma, q, type_option,
        chocs=list(np.linspace(-0.30, 0.30, 25)), quantite=quantite
    )
    noms_courbes = ["P&L réel (reprix)", "Delta + gamma", "Delta seul"]
    cles = ["pnl_reel", "pnl_estime", "pnl_delta_seul"]
    points = []
    for ligne in lignes:
        for nom, cle in zip(noms_courbes, cles):
            points.append({"Choc de spot (%)": float(ligne["choc_spot"]) * 100, "P&L (€)": ligne[cle], "Courbe": nom})

    courbes = alt.Chart(pd.DataFrame(points)).mark_line().encode(
        x=alt.X("Choc de spot (%):Q"),
        y=alt.Y("P&L (€):Q", title="P&L (€)"),
        color=alt.Color("Courbe:N", title=None,
                        scale=alt.Scale(domain=noms_courbes, range=["#1f77b4", "#ff7f0e", "#2ca02c"]),
                        legend=alt.Legend(orient="top-left", labelLimit=0)),
        strokeDash=alt.StrokeDash("Courbe:N", legend=None,
                                  scale=alt.Scale(domain=noms_courbes, range=[[1, 0], [6, 4], [2, 2]])),
        tooltip=["Courbe:N", alt.Tooltip("Choc de spot (%):Q", format="+.1f"), alt.Tooltip("P&L (€):Q", format="+.4f")],
    )
    zero = alt.Chart(pd.DataFrame([{"y": 0}])).mark_rule(color="grey").encode(y="y:Q")
    st.altair_chart((courbes + zero).properties(height=350), width=700)
