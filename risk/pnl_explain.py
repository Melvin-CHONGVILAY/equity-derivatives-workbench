# risk/pnl_explain.py
# Phase 6 : Hedge & P&L Explain
#
# Idée : après un mouvement de marché, on calcule le P&L de deux façons
#   1) P&L "réel"   : on reprice l'option complètement avant / après
#   2) P&L "estimé" : on utilise seulement les Greeks (développement de Taylor)
#      Δ·ΔS + ½·Γ·ΔS² + Θ·Δt + Vega·Δσ + ρ·Δr
# L'écart entre les deux (le "résidu") vient des termes d'ordre supérieur.
#
# Unités (cohérentes avec greeks.py) :
#   - choc_spot  : relatif   (-0.10 = spot -10%)
#   - choc_vol   : absolu    (0.05 = +5 points de vol)
#   - choc_taux  : absolu    (0.005 = +50 bps)
#   - jours      : jours calendaires qui passent (theta est annuel, donc /365)
#   - quantite   : nombre d'options (positif = long, négatif = short)

from pricing.black_scholes import prix_call, prix_put
from greeks.greeks import (
    delta_call, gamma_call, vega_call, theta_call, rho_call,
    delta_put, gamma_put, vega_put, theta_put, rho_put
)

JOURS_PAR_AN = 365


def verifier_type_option(type_option):
    if type_option not in ("call", "put"):
        raise ValueError(
            "Le type d'option doit être 'call' ou 'put'."
        )


def prix_option(S, K, T, r, sigma, q, type_option):
    verifier_type_option(type_option)

    if type_option == "call":
        return prix_call(S, K, T, r, sigma, q)

    return prix_put(S, K, T, r, sigma, q)


def greeks_option(S, K, T, r, sigma, q, type_option):
    verifier_type_option(type_option)

    if type_option == "call":
        return {
            "delta": float(delta_call(S, K, T, r, sigma, q)),
            "gamma": float(gamma_call(S, K, T, r, sigma, q)),
            "vega": float(vega_call(S, K, T, r, sigma, q)),
            "theta": float(theta_call(S, K, T, r, sigma, q)),
            "rho": float(rho_call(S, K, T, r, sigma, q))
        }

    return {
        "delta": float(delta_put(S, K, T, r, sigma, q)),
        "gamma": float(gamma_put(S, K, T, r, sigma, q)),
        "vega": float(vega_put(S, K, T, r, sigma, q)),
        "theta": float(theta_put(S, K, T, r, sigma, q)),
        "rho": float(rho_put(S, K, T, r, sigma, q))
    }


def marche_apres_choc(S, T, r, sigma, choc_spot, choc_vol, choc_taux, jours):
    # Calcule les nouveaux paramètres de marché après le mouvement
    S_apres = S * (1 + choc_spot)
    sigma_apres = sigma + choc_vol
    r_apres = r + choc_taux
    dt = jours / JOURS_PAR_AN
    T_apres = T - dt

    if S_apres <= 0:
        raise ValueError(
            "Le spot après choc doit être strictement positif."
        )

    if sigma_apres <= 0:
        raise ValueError(
            "La volatilité après choc doit être strictement positive."
        )

    if jours < 0:
        raise ValueError(
            "Le nombre de jours doit être positif ou nul."
        )

    if T_apres <= 0:
        raise ValueError(
            "La maturité restante doit rester strictement positive."
        )

    return S_apres, sigma_apres, r_apres, T_apres, dt


def pnl_reel(
    S, K, T, r, sigma, q, type_option,
    choc_spot=0.0, choc_vol=0.0, choc_taux=0.0, jours=0, quantite=1
):
    S_apres, sigma_apres, r_apres, T_apres, dt = marche_apres_choc(
        S, T, r, sigma, choc_spot, choc_vol, choc_taux, jours
    )

    prix_avant = prix_option(S, K, T, r, sigma, q, type_option)
    prix_apres = prix_option(
        S_apres, K, T_apres, r_apres, sigma_apres, q, type_option
    )

    return {
        "prix_avant": prix_avant,
        "prix_apres": prix_apres,
        "pnl_reel": (prix_apres - prix_avant) * quantite
    }


def pnl_estime_greeks(
    S, K, T, r, sigma, q, type_option,
    choc_spot=0.0, choc_vol=0.0, choc_taux=0.0, jours=0, quantite=1
):
    # Même contrôle que pour le reprix, pour avoir exactement le même scénario
    marche_apres_choc(S, T, r, sigma, choc_spot, choc_vol, choc_taux, jours)

    greeks = greeks_option(S, K, T, r, sigma, q, type_option)

    dS = S * choc_spot              # variation du spot en euros
    dt = jours / JOURS_PAR_AN       # temps écoulé en années

    contributions = {
        "delta": greeks["delta"] * dS * quantite,
        "gamma": 0.5 * greeks["gamma"] * dS ** 2 * quantite,
        "theta": greeks["theta"] * dt * quantite,
        "vega": greeks["vega"] * choc_vol * quantite,
        "rho": greeks["rho"] * choc_taux * quantite
    }

    pnl_estime = 0.0
    for valeur in contributions.values():
        pnl_estime = pnl_estime + valeur

    return {
        "greeks": greeks,
        "contributions": contributions,
        "pnl_estime": pnl_estime
    }


def commenter_ecart(ecart_pourcentage, contributions, choc_spot):
    # Terme qui pèse le plus dans le P&L estimé
    terme_dominant = None
    plus_grand = 0.0
    for nom, valeur in contributions.items():
        if abs(valeur) > plus_grand:
            plus_grand = abs(valeur)
            terme_dominant = nom

    if terme_dominant is None:
        return "Aucun choc de marché : le P&L est nul, il n'y a rien à expliquer."

    if ecart_pourcentage is None:
        return (
            "Le P&L réel est quasi nul : l'écart en % n'a pas de sens, "
            "il faut regarder l'écart en euros."
        )

    ecart_abs = abs(ecart_pourcentage)

    if ecart_abs < 2:
        texte = (
            "Écart très faible : le mouvement est petit, "
            "l'approximation locale par les Greeks est quasi exacte."
        )
    elif ecart_abs < 10:
        texte = (
            "Écart modéré : les termes d'ordre supérieur (convexité au-delà du gamma, "
            "effets croisés spot/vol) commencent à compter."
        )
    else:
        texte = (
            "Écart important : le mouvement est trop grand pour une approximation locale. "
            "Les Greeks sont calculés au point de départ et ne décrivent plus bien le prix "
            "après le choc, seul le reprix complet est fiable."
        )

    if abs(choc_spot) >= 0.10 and ecart_abs >= 2:
        texte = texte + (
            " Avec un choc de spot d'au moins 10%, la convexité joue à plein : "
            "le gamma lui-même change quand le spot bouge."
        )

    texte = texte + " Terme dominant du P&L estimé : " + terme_dominant + "."

    return texte


def pnl_explain(
    S, K, T, r, sigma, q, type_option,
    choc_spot=0.0, choc_vol=0.0, choc_taux=0.0, jours=0, quantite=1
):
    reel = pnl_reel(
        S, K, T, r, sigma, q, type_option,
        choc_spot, choc_vol, choc_taux, jours, quantite
    )

    estime = pnl_estime_greeks(
        S, K, T, r, sigma, q, type_option,
        choc_spot, choc_vol, choc_taux, jours, quantite
    )

    # Résidu = ce que les Greeks n'expliquent pas
    ecart = reel["pnl_reel"] - estime["pnl_estime"]

    if abs(reel["pnl_reel"]) < 1e-10:
        ecart_pourcentage = None
    else:
        ecart_pourcentage = (ecart / abs(reel["pnl_reel"])) * 100

    commentaire = commenter_ecart(
        ecart_pourcentage,
        estime["contributions"],
        choc_spot
    )

    return {
        "prix_avant": reel["prix_avant"],
        "prix_apres": reel["prix_apres"],
        "pnl_reel": reel["pnl_reel"],
        "pnl_estime": estime["pnl_estime"],
        "contributions": estime["contributions"],
        "greeks": estime["greeks"],
        "ecart": ecart,
        "ecart_pourcentage": ecart_pourcentage,
        "commentaire": commentaire
    }


def pnl_couverture_delta(
    S, K, T, r, sigma, q, type_option,
    choc_spot=0.0, choc_vol=0.0, choc_taux=0.0, jours=0, quantite=1
):
    # On couvre le delta au départ avec des actions, puis on laisse le marché bouger.
    # Simplification : on ignore le coût de financement et les dividendes de la couverture.
    resultat = pnl_explain(
        S, K, T, r, sigma, q, type_option,
        choc_spot, choc_vol, choc_taux, jours, quantite
    )

    S_apres = S * (1 + choc_spot)
    delta = resultat["greeks"]["delta"]

    # Long call (delta > 0) -> on vend des actions pour être neutre
    nb_actions = -delta * quantite
    pnl_actions = nb_actions * (S_apres - S)

    pnl_total_couvert = resultat["pnl_reel"] + pnl_actions

    # Une fois le delta neutralisé, il reste gamma + theta + vega + rho
    pnl_estime_couvert = resultat["pnl_estime"] - resultat["contributions"]["delta"]

    return {
        "nb_actions_couverture": nb_actions,
        "pnl_option": resultat["pnl_reel"],
        "pnl_actions": pnl_actions,
        "pnl_total_couvert": pnl_total_couvert,
        "pnl_estime_couvert": pnl_estime_couvert
    }


def balayage_chocs_spot(
    S, K, T, r, sigma, q, type_option,
    chocs=None, jours=0, quantite=1
):
    # Pour une série de chocs de spot : P&L réel vs P&L estimé
    # (c'est ce qui montre que l'écart grandit avec la taille du choc)
    if chocs is None:
        chocs = [-0.20, -0.15, -0.10, -0.05, -0.02, 0.0,
                 0.02, 0.05, 0.10, 0.15, 0.20]

    lignes = []

    for choc in chocs:
        resultat = pnl_explain(
            S, K, T, r, sigma, q, type_option,
            choc_spot=choc, jours=jours, quantite=quantite
        )

        lignes.append({
            "choc_spot": choc,
            "pnl_reel": resultat["pnl_reel"],
            "pnl_estime": resultat["pnl_estime"],
            "pnl_delta_seul": resultat["contributions"]["delta"],
            "ecart": resultat["ecart"],
            "ecart_pourcentage": resultat["ecart_pourcentage"]
        })

    return lignes


def afficher_pnl_explain(resultat):
    print(f"Prix avant           : {resultat['prix_avant']:.4f}")
    print(f"Prix après           : {resultat['prix_apres']:.4f}")
    print()
    print("Contributions des Greeks :")
    for nom, valeur in resultat["contributions"].items():
        print(f"  {nom:<6}: {valeur:+.4f}")
    print()
    print(f"P&L estimé (Greeks)  : {resultat['pnl_estime']:+.4f}")
    print(f"P&L réel (reprix)    : {resultat['pnl_reel']:+.4f}")
    print(f"Écart (résidu)       : {resultat['ecart']:+.4f}")

    if resultat["ecart_pourcentage"] is not None:
        print(f"Écart en % du réel   : {resultat['ecart_pourcentage']:+.2f} %")

    print()
    print(resultat["commentaire"])


def tracer_balayage(lignes, titre="P&L réel vs P&L estimé selon le choc de spot"):
    # matplotlib importé ici pour que le reste du fichier marche sans écran
    import matplotlib.pyplot as plt

    chocs = [ligne["choc_spot"] * 100 for ligne in lignes]
    reel = [ligne["pnl_reel"] for ligne in lignes]
    estime = [ligne["pnl_estime"] for ligne in lignes]
    delta_seul = [ligne["pnl_delta_seul"] for ligne in lignes]

    plt.figure(figsize=(8, 5))
    plt.plot(chocs, reel, label="P&L réel (reprix complet)", linewidth=2)
    plt.plot(chocs, estime, "--", label="P&L estimé (delta + gamma)")
    plt.plot(chocs, delta_seul, ":", label="Delta seul")
    plt.axhline(0, color="grey", linewidth=0.8)
    plt.xlabel("Choc de spot (%)")
    plt.ylabel("P&L (€)")
    plt.title(titre)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    # Call ATM 1 an, même cas que dans black_scholes.py
    S, K, T, r, sigma, q = 100, 100, 1, 0.02, 0.20, 0.0

    print("=== Petit mouvement : spot +1%, vol +0.5 pt, 1 jour ===")
    petit = pnl_explain(
        S, K, T, r, sigma, q, "call",
        choc_spot=0.01, choc_vol=0.005, jours=1
    )
    afficher_pnl_explain(petit)

    print()
    print("=== Gros mouvement : spot -15%, vol +5 pts, 5 jours ===")
    gros = pnl_explain(
        S, K, T, r, sigma, q, "call",
        choc_spot=-0.15, choc_vol=0.05, jours=5
    )
    afficher_pnl_explain(gros)

    print()
    print("=== Couverture delta (spot -5%, 1 jour) ===")
    couverture = pnl_couverture_delta(
        S, K, T, r, sigma, q, "call",
        choc_spot=-0.05, jours=1
    )
    for nom, valeur in couverture.items():
        print(f"  {nom:<22}: {valeur:+.4f}")

    print()
    print("=== Balayage du choc de spot ===")
    balayage = balayage_chocs_spot(S, K, T, r, sigma, q, "call")
    for ligne in balayage:
        print(
            f"  spot {ligne['choc_spot'] * 100:+6.1f}% | "
            f"réel {ligne['pnl_reel']:+8.4f} | "
            f"estimé {ligne['pnl_estime']:+8.4f} | "
            f"écart {ligne['ecart']:+8.4f}"
        )

    tracer_balayage(balayage)