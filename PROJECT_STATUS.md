# Equity Derivatives Workbench — État du projet

Dernière mise à jour : 27 septembre 2026

## Objectif

Portfolio Python de dérivés actions pour une recherche de stage en avril 2027 et support
d’apprentissage en pricing, Greeks, Monte Carlo, risk et PnL Explain.

## Phase actuelle

Phase 4 — Monte Carlo pour l’autocall.

## Phases terminées

- Phase 0 : environnement, Git et venv
- Phase 1 : Black-Scholes
- Phase 2 : payoff et PnL call/put
- Phase 3 : Greeks analytiques et Delta numérique

## Fichiers existants

### pricing/black_scholes.py

Fonctions existantes :

- `calculer_d1_d2(S, K, T, r, sigma, q)`
- `prix_call(S, K, T, r, sigma, q)`
- `prix_put(S, K, T, r, sigma, q)`

### pricing/payoff.py

Fonctions existantes :

- `calculer_call_payoff`
- `calculer_put_payoff`
- `calculer_call_PnL`
- `calculer_put_PnL`
- Fonction de tracé protégée par `if __name__ == "__main__":`

### greeks/greeks.py

Greeks analytiques :

- `delta_call`
- `delta_put`
- `gamma_call`
- `gamma_put`
- `vega_call`
- `vega_put`
- `theta_call`
- `theta_put`
- `rho_call`
- `rho_put`

Différences finies :

- `delta_call_num`
- `delta_put_num`

Convention des paramètres :

`(S, K, T, r, sigma, q=0.0)`

### monte_carlo/autocall.py

Fonction existante :

`simuler_trajectoires(S0, T, r, sigma, q=0.0,
                      n_trajectoires=100, n_pas=12, seed=None)`

Fonctionnement :

- Calcul de `dt = T / n_pas`
- Génération vectorisée des chocs normaux
- Drift risque-neutre
- Diffusion
- Cumul des log-rendements avec `np.cumsum(..., axis=1)`
- Transformation en prix avec `np.exp`
- Retour d’une matrice `(n_trajectoires, n_pas + 1)`
- Première colonne égale au spot initial

## Tests existants

### tests/test_payoff.py

- Call ITM, OTM et break-even
- Put ITM, OTM et break-even
- Cas `S_T = K`
- Payoff et PnL

### tests/test_greeks.py

- Delta call analytique contre numérique
- Delta put analytique contre numérique
- Delta call compris entre 0 et 1
- Delta put compris entre -1 et 0

### tests/test_autocall.py

Premier test structurel :

- Forme attendue `(100, 13)`
- Première colonne proche de `S0` avec `np.allclose`

## Dernière étape réalisée

Création du moteur vectorisé de trajectoires par mouvement brownien géométrique et
du premier test de structure.

## Étape à valider

Lancer :

`python -m pytest tests/test_autocall.py -v`

Vérifier que le test passe avec :

- `resultat_trajectoires.shape == (100, 13)`
- `np.allclose(resultat_trajectoires[:, 0], S0)`

## Prochaine étape

Tracer seulement 5 à 10 trajectoires pour vérifier visuellement :

- Toutes commencent à `S0`
- Elles restent positives
- Elles évoluent de façon plausible
- L’axe temporel va de 0 à T

Ensuite, définir le term sheet précis de l’autocall simplifié avant de coder le payoff.

## Pas encore fait

- Dates d’observation
- Barrière de rappel
- Coupons
- Barrière de protection
- Perte en capital
- Actualisation des cash-flows
- Prix Monte Carlo
- Probabilité de rappel
- Probabilité de perte
- Test de convergence

## Workflow

- Mac et Windows
- Synchronisation par GitHub
- Un venv distinct par machine
- `venv/` dans `.gitignore`
- `requirements.txt` partagé