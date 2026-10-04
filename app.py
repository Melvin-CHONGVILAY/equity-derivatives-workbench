# app.py
# Interface Streamlit du projet : lancer avec "streamlit run app.py" depuis la racine.
# L'app ne contient pas de formule : elle appelle uniquement les modules du projet.

import io
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import streamlit as st

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
def autocall_cache(S0, T, r, sigma, q, n_trajectoires, seed):
    return valoriser_autocall(S0, T, r, sigma, q, n_trajectoires=n_trajectoires, seed=seed)


@st.cache_data
def convergence_cache(S0, T, r, sigma, q, seed):
    return analyser_convergence(S0, T, r, sigma, q, seed=seed)


@st.cache_data
def stress_autocall_cache(S0, T, r, sigma, q, n_trajectoires, seed, chocs_spot, chocs_vol):
    lignes = []
    for choc in chocs_spot:
        res = stress_spot_autocall(S0, T, r, sigma, q, choc, n_trajectoires, seed)
        lignes.append({"scénario": f"spot {choc * 100:+.0f}%", **res})
    for choc in chocs_vol:
        res = stress_vol_autocall(S0, T, r, sigma, q, choc, n_trajectoires, seed)
        lignes.append({"scénario": f"vol {choc * 100:+.0f} pts", **res})
    return lignes


def afficher_graphique(fig):
    # On n'utilise pas st.pyplot : il étire l'image sur toute la page et recadre la
    # figure ("tight"), donc la taille change avec la fenêtre et les valeurs.
    # Ici la figure est enregistrée en PNG à taille fixe (figsize x dpi),
    # puis affichée avec une largeur fixe de 700 px.
    fig.tight_layout()
    image = io.BytesIO()
    fig.savefig(image, format="png", dpi=200)
    plt.close(fig)
    st.image(image, width=700)


onglet_pricing, onglet_autocall, onglet_scenarios, onglet_pnl = st.tabs([
    "Pricing & Greeks", "Autocall Monte Carlo", "Scénarios de marché", "Hedge & P&L Explain"
])


# --- Onglet 1 : Pricing & Greeks --------------------------------------------

with onglet_pricing:
    prix = prix_option(S, K, T, r, sigma, q, type_option)
    greeks = greeks_option(S, K, T, r, sigma, q, type_option)

    col1, col2 = st.columns(2)
    col1.metric(f"Prix du {type_option} (Black-Scholes)", f"{prix:.4f}")
    col2.metric("Parité call-put : C - P", f"{prix_call(S, K, T, r, sigma, q) - prix_put(S, K, T, r, sigma, q):.4f}",
                help="Doit être égal à S·exp(-qT) - K·exp(-rT)")

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
    nom_prix = f"Prix Black-Scholes (T = {T:g} an)"
    points = []
    for s, p, v in zip(spots, prix_spots, payoff):
        points.append({"Spot": float(s), "Valeur": float(p), "Courbe": nom_prix})
        points.append({"Spot": float(s), "Valeur": float(v), "Courbe": "Payoff à maturité"})

    # Axes fixés par rapport au strike, avec une petite marge sous 0
    # pour bien voir les courbes qui sont à y = 0
    haut = max(0.6 * K, max(prix_spots) * 1.05)
    echelle_x = alt.Scale(domain=[0.5 * K, 1.5 * K])
    echelle_y = alt.Scale(domain=[-0.05 * haut, haut])

    courbes = alt.Chart(alt.Data(values=points)).mark_line(clip=True).encode(
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
    base_reperes = alt.Chart(alt.Data(values=reperes)).encode(
        x=alt.X("Spot:Q", scale=echelle_x),
        color=alt.Color("couleur:N", scale=None),
    )
    lignes_verticales = base_reperes.mark_rule(strokeDash=[3, 3])
    # hauteur_texte en pixels (scale=None) : les deux étiquettes ne se chevauchent pas si S = K
    textes = base_reperes.mark_text(align="left", dx=4).encode(
        text="Repère:N", y=alt.Y("hauteur_texte:Q", scale=None)
    )

    zero = alt.Chart(alt.Data(values=[{"y": 0}])).mark_rule(color="grey", opacity=0.5).encode(y="y:Q")

    graphique = (courbes + lignes_verticales + textes + zero).properties(height=350)
    # Largeur fixe : même taille sur un petit ou un grand écran
    st.altair_chart(graphique, width=700)

    if not 0.5 * K <= S <= 1.5 * K:
        st.caption("Le spot actuel est hors de la zone affichée (50% à 150% du strike).")

    st.subheader("Volatilité implicite")
    st.write("Le marché cote les options en vol : on retrouve σ à partir d'un prix observé (Newton-Raphson).")
    prix_marche = st.number_input("Prix de marché observé", min_value=0.0, value=round(prix, 4), step=0.1)
    try:
        vol_implicite = implied_vol(prix_marche, S, K, T, r, type_option, q=q)
        st.metric("Volatilité implicite", f"{vol_implicite * 100:.2f} %")
    except (ValueError, RuntimeError) as erreur:
        st.error(str(erreur))


# --- Onglet 2 : Autocall Monte Carlo ----------------------------------------

with onglet_autocall:
    st.write(
        "Autocall simplifié 1 an sur nominal = S0 : observations trimestrielles, rappel si S ≥ S0 "
        "avec coupon de 2% par trimestre, protection du capital tant que S_T ≥ 60% de S0. "
        "Le prix est la moyenne des cash-flows actualisés sur les trajectoires simulées."
    )
    col1, col2 = st.columns(2)
    n_trajectoires = col1.select_slider(
        "Nombre de trajectoires", options=[1000, 5000, 10000, 50000, 100000], value=50000
    )
    seed = col2.number_input("Seed", min_value=0, value=42, step=1)

    resultat = autocall_cache(S, T, r, sigma, q, n_trajectoires, seed)

    col1, col2, col3 = st.columns(3)
    col1.metric("Prix Monte Carlo", f"{resultat['prix']:.3f}")
    col2.metric("Erreur standard", f"{resultat['erreur_standard']:.4f}")
    col3.metric("IC 95%", f"[{resultat['borne_basse_95']:.2f} ; {resultat['borne_haute_95']:.2f}]")

    col1, col2 = st.columns(2)
    col1.metric("Probabilité de rappel anticipé", f"{resultat['probabilite_rappel_anticipe'] * 100:.1f} %")
    col2.metric("Probabilité de perte en capital", f"{resultat['probabilite_perte_capital'] * 100:.2f} %")

    dates = ["3 mois", "6 mois", "9 mois", "12 mois"]
    probas = [resultat[f"probabilite_rappel_mois_{m}"] for m in (3, 6, 9, 12)]
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.bar(dates, [p * 100 for p in probas])
    ax.set_ylabel("Probabilité (%)")
    ax.set_title("Probabilité de rappel à chaque date d'observation")
    ax.grid(axis="y", alpha=0.3)
    afficher_graphique(fig)

    st.subheader("Convergence")
    st.write("L'erreur standard diminue en 1/√N : 4 fois plus de trajectoires divisent l'erreur par 2.")
    st.dataframe(convergence_cache(S, T, r, sigma, q, seed), hide_index=True, width="stretch")


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
    st.dataframe(lignes, hide_index=True, width="stretch")

    st.subheader("Stress test de l'autocall")
    st.write("Mêmes trajectoires avant et après choc (même seed) : la variation mesure le choc et pas le bruit Monte Carlo.")
    n_stress = st.select_slider("Trajectoires pour le stress", options=[5000, 20000, 50000], value=20000)
    chocs_vol_autocall = tuple(c for c in (-0.05, 0.05, 0.10) if sigma + c > 0)
    lignes_autocall = stress_autocall_cache(S, T, r, sigma, q, n_stress, 42, (-0.20, -0.10, 0.10), chocs_vol_autocall)
    st.dataframe(lignes_autocall, hide_index=True, width="stretch")


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
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.bar(noms, valeurs, color=["tab:blue"] * 5 + ["tab:red"])
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.set_ylabel("P&L (€)")
    ax.set_title("Décomposition du P&L par Greek")
    ax.grid(axis="y", alpha=0.3)
    afficher_graphique(fig)

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
    lignes = balayage_chocs_spot(
        S, K, T, r, sigma, q, type_option,
        chocs=list(np.linspace(-0.30, 0.30, 25)), quantite=quantite
    )
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot([l["choc_spot"] * 100 for l in lignes], [l["pnl_reel"] for l in lignes], label="P&L réel (reprix)", linewidth=2)
    ax.plot([l["choc_spot"] * 100 for l in lignes], [l["pnl_estime"] for l in lignes], "--", label="Delta + gamma")
    ax.plot([l["choc_spot"] * 100 for l in lignes], [l["pnl_delta_seul"] for l in lignes], ":", label="Delta seul")
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.set_xlabel("Choc de spot (%)")
    ax.set_ylabel("P&L (€)")
    ax.legend(fontsize="small")
    ax.grid(alpha=0.3)
    afficher_graphique(fig)
