Equity Derivatives Workbench — État du projet
Dernière mise à jour : 8 octobre 2026

Objectif
Portfolio Python de dérivés actions pour une recherche de stage en avril 2027 et support
d’apprentissage en pricing, Greeks, Monte Carlo, risk et PnL Explain.

Phase actuelle
Phases 0 à 9 codées, testées et finalisées. Reste : déployer l'app sur Streamlit Community Cloud
et ajouter le lien en haut du README et dans le CV.
Prochaine phase : Phase 10 — préparation aux questions d'entretien.

Phases terminées
Phase 0 : environnement, Git et venv

Phase 1 : Black-Scholes

Phase 2 : payoff et PnL call/put

Phase 3 : Greeks analytiques et Delta numérique

Phase 4 : Monte Carlo vectorisé pour un autocall simplifié

Phase 5 : scénarios de marché et stress tests (call, put, autocall)

Phase 6 : Hedge & P&L Explain

Phase 7 : consolidation des tests

Phase 8 : app Streamlit (prête à déployer)

Phase 9 : README (lien de l'app à ajouter après le déploiement)

Fichiers existants
pricing/black_scholes.py
Fonctions existantes :

calculer_d1_d2(S, K, T, r, sigma, q)

prix_call(S, K, T, r, sigma, q)

prix_put(S, K, T, r, sigma, q)

pricing/payoff.py
Fonctions existantes :

calculer_call_payoff

calculer_put_payoff

calculer_call_PnL

calculer_put_PnL

Fonction de tracé protégée par if __name__ == "__main__":

greeks/greeks.py
Greeks analytiques :

delta_call

delta_put

gamma_call

gamma_put

vega_call

vega_put

theta_call

theta_put

rho_call

rho_put

Différences finies :

delta_call_num

delta_put_num

Conventions vérifiées contre des différences finies :

Vega : dV/dsigma pour sigma en décimal (choc de 0.01 = 1 point de vol, vega/100 = par point)

Theta : annuel, en temps calendaire, theta = -dV/dT (1 jour = theta/365)

Rho : dV/dr pour r en décimal (choc de 0.001 = 10 bps)

Convention des paramètres :

(S, K, T, r, sigma, q=0.0)

monte_carlo/autocall.py
Fonctions existantes :

simuler_trajectoires(...)

tracer_trajectoires(...)

autocall(...)

dates_paiement_autocall(...)

cashflow_final_actualise(...)

autocall_actualise(...)

statistiques_autocall(...)

valoriser_autocall(...)

analyser_convergence(...)

Fonctionnement :

Simulation vectorisée d’un mouvement brownien géométrique sous la mesure risque-neutre

Générateur np.random.default_rng(seed) pour la reproductibilité

Matrice de trajectoires de forme (n_trajectoires, n_pas + 1)

Première colonne exactement égale à S0

Trajectoires strictement positives

S0 = niveau initial du term sheet (nominal, seuil de rappel, barrière) ;
spot = niveau du sous-jacent aujourd'hui, point de départ des trajectoires (S0 par défaut)

4 dates d'observation : T/4, T/2, 3T/4 et T (3, 6, 9 et 12 mois pour T = 1 an)

Rappel si le sous-jacent est supérieur ou égal au seuil de rappel (100% de S0)

Coupon de 2% du nominal par date d'observation écoulée, payé au rappel (102, 104, 106 ou 108)

Sans rappel : nominal seul (100) si le niveau final est supérieur ou égal à 60% de S0

Participation à la baisse sous la barrière de protection (nominal × S_T / S0)

Dates de paiement égales à 0.25·T, 0.50·T, 0.75·T ou T

Actualisation continue des cash-flows avec np.exp(-r * t)

Prix Monte Carlo obtenu par moyenne des cash-flows actualisés

Calcul de l’erreur standard et d’un intervalle de confiance approximatif à 95%

Probabilités de rappel par date, de rappel anticipé et de perte en capital

Analyse de convergence pour plusieurs nombres de trajectoires

pricing/implied_vol.py
Fonction existante :

implied_vol(prix_marche, S, K, T, r, type_option, sigma_initiale=0.20, q=0, ...)

Newton-Raphson avec contrôle des bornes de non-arbitrage et garde-fou si le pas sort de ]0 ; 5]

Refus explicite si la valeur temps est quasi nulle (< 1e-6) : la vol n'est alors pas identifiable

risk/scenarios.py
Fonctions existantes :

stress_spot_call, stress_spot_put, stress_vol_call, stress_vol_put

stress_vol_autocall, stress_spot_autocall (même seed avant/après : nombres aléatoires communs,
paramètre spot pour partir du spot du jour avec le term sheet S0)

calculer_variation et comparer_autocall : calcul commun de la variation en € et en %

risk/pnl_explain.py
Fonctions existantes :

prix_option, greeks_option, marche_apres_choc

pnl_reel : full repricing, prix après - prix avant

pnl_estime_greeks : Δ·ΔS + ½·Γ·ΔS² + Θ·Δt + Vega·Δσ + ρ·Δr

pnl_explain : réel, estimé, contributions, écart, écart en % (None si P&L réel nul), commentaire

pnl_couverture_delta : couverture delta statique avec des actions

balayage_chocs_spot, afficher_pnl_explain, tracer_balayage

Unités des chocs : choc_spot relatif, choc_vol et choc_taux absolus, jours calendaires (Δt = jours/365),
quantite positive = long, négative = short.

Périmètre : call et put Black-Scholes uniquement (pas de P&L Explain autocall).

app.py
Interface Streamlit, 4 onglets : Pricing & Greeks (+ vol implicite), Autocall Monte Carlo,
Scénarios de marché, Hedge & P&L Explain. Lancement : streamlit run app.py

5 graphiques Altair (payoff, rappel par date, stress du call/put, décomposition du P&L, balayage).
Autocall : le strike K sert de niveau initial S0, le spot S est le point de départ ; prix, erreur
standard et IC affichés en % du nominal. Le stress de l'autocall utilise le même term sheet et la
même seed que l'onglet Autocall.

Tests existants
tests/test_payoff.py
Call ITM, OTM et break-even

Put ITM, OTM et break-even

Cas S_T = K

Payoff et PnL

tests/test_greeks.py
Delta call analytique contre numérique

Delta put analytique contre numérique

Delta call compris entre 0 et 1

Delta put compris entre -1 et 0

Gamma, vega, theta, rho analytiques contre différences finies (call et put)

Gamma et vega identiques call/put, parité sur le delta

tests/test_black_scholes.py
Parité call-put (avec et sans dividende)

Vol quasi nulle, maturité très courte, spot = strike, bornes du prix, prix croissant avec la vol

Refus des paramètres invalides (T = 0, sigma <= 0, spot nul)

Vol implicite sur plusieurs strikes (dont un call très ITM) et refus d'un prix hors bornes

tests/test_scenarios.py
Stress spot et vol sur call, put et autocall

Parité call-put respectée par les stress de spot, même variation call/put pour un choc de vol

Stress autocall avec un spot du jour différent de S0

tests/test_pnl_explain.py (34 tests)
Aucun choc, sens du P&L call/put, cohérence reprix et somme des contributions, quantité

Unité de chaque contribution (delta, gamma, vega, rho, theta) contre le reprix complet

Petit choc (résidu < 2% du P&L réel), gamma améliore le delta seul, gros choc cohérent

Couverture delta (un call long couvert gagne sur un mouvement de spot), balayage

Paramètres invalides

tests/test_app.py
L'app Streamlit se lance sans exception, cas put + gros choc, message d'erreur si maturité dépassée

Les données envoyées à chaque graphique sont comparées aux modules (Black-Scholes, autocall,
stress, P&L Explain, balayage) et aux métriques affichées

Les dates du graphique de rappel suivent la maturité, la probabilité de rappel suit le spot,
le prix avant choc du stress autocall est celui de l'onglet Autocall

tests/test_autocall.py
Tests validés :

Forme attendue des trajectoires

Première colonne égale à S0

Positivité et dispersion des trajectoires

Rappel aux mois 3 et 6

Cas de maturité protégée

Perte en capital sous la barrière

Frontière de protection exactement à 60% de S0

Actualisation d’un cash-flow

Dates de paiement 0.25, 0.50, 0.75 et 1.00 an

Assemblage du cash-flow actualisé

Reproductibilité avec une seed fixe

Probabilités comprises entre 0 et 1

Cohérence entre les probabilités de rappel par date et les probabilités agrégées

Cas déterministe avec volatilité nulle

Cohérence de l’intervalle de confiance

Diminution de l’erreur standard lorsque le nombre de trajectoires augmente

Spot du jour différent de S0 : invariance d'échelle, moins de rappel et plus de perte quand le spot baisse

Rappel à la dernière date avec 4 coupons (108)

Probabilité de rappel à la 1re date contre la formule fermée N(d)

Le moteur de simulation retrouve le prix Black-Scholes d'un call européen et le forward

Valeurs de référence du README

Commande de validation :

python -m pytest tests/test_autocall.py -v

Résultat : tous les tests de la Phase 4 passent.

Dernière étape réalisée
Finalisation le 8 octobre 2026 : relecture complète, corrections et tests de cohérence des graphiques.

Commande de validation : python -m pytest -v (ou pytest)

Résultat : 159 tests passent.

Bugs corrigés le 8 octobre :

Onglet Autocall : prix en % du nominal mais erreur standard, IC et convergence en € ;
tout est maintenant en % du nominal

Libellés "3 mois ... 12 mois" et texte "1 an, trimestriel" figés : ils suivent maintenant la maturité T

Stress de l'autocall : partait du spot S comme niveau initial alors que l'onglet Autocall utilise K ;
même term sheet (S0 = K, spot = S) et même seed partout

Graphique de rappel figé quand seules les données changeaient (alt.Data) : remplacé par des DataFrame

Tableaux de stress illisibles (clés brutes, probabilités en fraction) : colonnes en français et en %

Vol implicite d'une option sans valeur temps (put très ITM, call très OTM à vol faible) : erreur "hors des bornes"
ou vol fausse (2.93% au lieu de 1%) ; message "valeur temps quasi nulle" à la place

Bugs corrigés avant :

Rappel anticipé insensible au spot (S servait de S0) : ajout du paramètre spot

Payoff protégé à maturité : nominal seul (100) et non nominal + coupons

theta_put appelait calculer_d1_d2(S, T, K, ...) au lieu de (S, K, T, ...) : theta du put faux
(+0.07 au lieu de -3.32 sur le cas ATM avec q = 1%), donc P&L Explain du put faux sur le terme theta

calculer_d1_d2 : division par zéro si T ou sigma = 0 et prix négatif sans erreur si sigma < 0,
remplacé par une ValueError explicite

implied_vol : Newton divergeait sur un call très ITM à vol élevée (vega faible au départ)

tracer_trajectoires s'appelait elle-même à la fin (récursion infinie)

pytest seul ne trouvait pas les modules : ajout de pytest.ini

Historique Phase 4 :
Phase 4 terminée le 1er octobre 2026.

Le pricer Monte Carlo de l’autocall simplifié simule les trajectoires, applique les règles
de rappel et de protection, actualise les cash-flows, calcule un prix moyen et fournit des
statistiques de risque ainsi qu’une analyse de convergence.

Exemple validé avec 50 000 trajectoires, S0=100, T=1, r=2 %, sigma=20 %,
q=0 et seed=42 :

Prix Monte Carlo : environ 100.88 (102.98 avant la correction du payoff protégé)

Erreur standard : environ 0.017

Intervalle de confiance approximatif à 95% : environ [100.85 ; 100.91]

Probabilité de rappel anticipé : environ 68.97%

Probabilité de perte en capital : environ 0.47%

Prochaine étape
Déployer l'app sur Streamlit Community Cloud et ajouter le lien en haut du README et dans le CV.

Phase 10 : questions d'entretien et fiches d'explication de chaque partie.

Problèmes ouverts
Aucun test en échec.

Pas de P&L Explain pour l'autocall (pas de Greeks analytiques, seulement des stress tests Monte Carlo).

La couverture delta est statique sur un pas (pas de rebalancement, financement ignoré).

La vol implicite n'est pas identifiable quand la valeur temps est quasi nulle (option très ITM/OTM à vol faible) : le module le signale au lieu de renvoyer une vol arbitraire.

PROJECT_STATUS.docx n'a pas été mis à jour (ce fichier .md fait foi).

Le term sheet reste volontairement simplifié : volatilité et taux constants, 4 dates d'observation, absence de smile, de calibration, de risque de crédit et de coûts de couverture.

Lancer régulièrement la suite complète avec python -m pytest -v pendant les phases suivantes.

Workflow
Mac et Windows

Synchronisation par GitHub

Un venv distinct par machine

venv/ dans .gitignore

requirements.txt partagé

Modules lancés depuis la racine avec python -m ...

Tests lancés avec python -m pytest -v (ou pytest grâce à pytest.ini)

App lancée avec streamlit run app.py