Equity Derivatives Workbench — État du projet
Dernière mise à jour : 1er octobre 2026

Objectif
Portfolio Python de dérivés actions pour une recherche de stage en avril 2027 et support
d’apprentissage en pricing, Greeks, Monte Carlo, risk et PnL Explain.

Phase actuelle
Phase 5 — Scénarios de marché et stress tests.

Phases terminées
Phase 0 : environnement, Git et venv

Phase 1 : Black-Scholes

Phase 2 : payoff et PnL call/put

Phase 3 : Greeks analytiques et Delta numérique

Phase 4 : Monte Carlo vectorisé pour un autocall simplifié

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

Observations trimestrielles aux mois 3, 6, 9 et 12

Rappel si le sous-jacent est supérieur ou égal au seuil de rappel

Coupon trimestriel de 2% du nominal

Protection du nominal si le niveau final est supérieur ou égal à 60% de S0

Participation à la baisse sous la barrière de protection

Dates de paiement égales à 0.25, 0.50, 0.75 ou 1.00 an

Actualisation continue des cash-flows avec np.exp(-r * t)

Prix Monte Carlo obtenu par moyenne des cash-flows actualisés

Calcul de l’erreur standard et d’un intervalle de confiance approximatif à 95%

Probabilités de rappel par date, de rappel anticipé et de perte en capital

Analyse de convergence pour plusieurs nombres de trajectoires

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

Commande de validation :

python -m pytest tests/test_autocall.py -v

Résultat : tous les tests de la Phase 4 passent.

Dernière étape réalisée
Phase 4 terminée le 1er octobre 2026.

Le pricer Monte Carlo de l’autocall simplifié simule les trajectoires, applique les règles
de rappel et de protection, actualise les cash-flows, calcule un prix moyen et fournit des
statistiques de risque ainsi qu’une analyse de convergence.

Exemple validé avec 50 000 trajectoires, S0=100, T=1, r=2 %, sigma=20 %,
q=0 et seed=42 :

Prix Monte Carlo : environ 102.98

Erreur standard : environ 0.017

Intervalle de confiance approximatif à 95% : environ [102.95 ; 103.02]

Probabilité de rappel anticipé : environ 68.97%

Probabilité de perte en capital : environ 0.47%

Prochaine étape
Commencer la Phase 5 dans risk/scenarios.py.

Première petite brique : repricer une option vanille après un choc du spot, puis retourner :

le prix avant choc ;

le prix après choc ;

la variation en euros ;

la variation en pourcentage.

Ensuite :

choc de volatilité ;

stress test de l’autocall ;

tableau récapitulatif des scénarios.

Problèmes ouverts
Aucun problème bloquant identifié pour la Phase 4.

Le term sheet reste volontairement simplifié : volatilité et taux constants, observations trimestrielles, absence de smile, de calibration, de risque de crédit et de coûts de couverture.

Lancer régulièrement la suite complète avec python -m pytest -v pendant les phases suivantes.

Workflow
Mac et Windows

Synchronisation par GitHub

Un venv distinct par machine

venv/ dans .gitignore

requirements.txt partagé

Modules lancés depuis la racine avec python -m ...

Tests lancés avec python -m pytest -v