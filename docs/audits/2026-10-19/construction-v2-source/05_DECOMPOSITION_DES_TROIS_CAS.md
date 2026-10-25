# Décomposition documentaire ADOPT / MAP / LAB

**24 nouvelles fiches candidates uniquement locales.** Elles ne remplacent pas les cas canoniques et n’altèrent pas CREATE déjà prouvé.

### ADOPT_EXISTING_REPOSITORY

1. `DRAFT-CASE-ADOPT-T01` — Observer HEAD, branches, protections, fichiers canoniques et points d’entrée → **Observation sourcée du dépôt existant**
2. `DRAFT-CASE-ADOPT-T02` — Inventorier modèles, workflows, mémoires, tests et gouvernance antérieurs → **Inventaire des éléments existants et inconnus**
3. `DRAFT-CASE-ADOPT-T03` — Comparer le dépôt au Governance Model commun → **Matrice de comparaison appliquée au cas ADOPT**
4. `DRAFT-CASE-ADOPT-T04` — Qualifier les éléments en REUSE, ADD, PRESERVE, CONFLICT_HOLD ou SKIP → **Décisions de compatibilité motivées**
5. `DRAFT-CASE-ADOPT-T05` — Élaborer une migration additive sans écraser les autorités existantes → **Plan de migration et de réversibilité**
6. `DRAFT-CASE-ADOPT-T06` — Définir exigences d’approbation, sauvegarde et exact-HEAD → **Contrat de gates avant écriture**
7. `DRAFT-CASE-ADOPT-T07` — Préparer les tests de non-régression et de sécurité du cas → **Matrice de tests et critères FAIL/HOLD**
8. `DRAFT-CASE-ADOPT-T08` — Définir preuve de recette E2E et handoff post-adoption → **Dossier d’acceptation et reprise du cas ADOPT**

### MAP_EXISTING_PROJECT

1. `DRAFT-CASE-MAP-T01` — Observer le projet réel en lecture seule, avec sources et versions → **Carte des observations sourcées**
2. `DRAFT-CASE-MAP-T02` — Extraire les composants, interfaces, stockage, déploiement, équipes et contraintes → **Inventaire CURRENT_ARCHITECTURE**
3. `DRAFT-CASE-MAP-T03` — Restituer l’architecture CURRENT indépendamment du TARGET → **Modèle CURRENT versionné**
4. `DRAFT-CASE-MAP-T04` — Charger les exigences et TARGET_ARCHITECTURE applicables → **Modèle TARGET versionné**
5. `DRAFT-CASE-MAP-T05` — Rapprocher CURRENT, TARGET et UNKNOWN sans fausse équivalence → **Matrice CURRENT→TARGET**
6. `DRAFT-CASE-MAP-T06` — Qualifier les GAPs, risques et dépendances → **GAP_MAP avec statuts et provenance**
7. `DRAFT-CASE-MAP-T07` — Définir la revue documentaire et les tests de non-mutation → **Contrats de conformité READ_ONLY**
8. `DRAFT-CASE-MAP-T08` — Préparer preuve E2E du cas MAP, restitution et checkpoint → **Rapport MAP et handoff**

### LAB_EVOLUTION

1. `DRAFT-CASE-LAB-T01` — Observer baseline canonique et éventuels LABs existants → **Baseline sourcée et LAB réutilisable ou absent**
2. `DRAFT-CASE-LAB-T02` — Délimiter expérimentation, hypothèses et composants autorisés → **Contrat de périmètre du LAB**
3. `DRAFT-CASE-LAB-T03` — Cartographier les autorisations de branche, PR, revue, CI et fusion → **Matrice des autorités LAB**
4. `DRAFT-CASE-LAB-T04` — Définir branche isolée sans seconde source de vérité → **Plan de branche et de protection du main**
5. `DRAFT-CASE-LAB-T05` — Décomposer les changements en contrats et tâches vérifiables → **Backlog LAB strictement borné**
6. `DRAFT-CASE-LAB-T06` — Définir tests/CI et comparaison baseline→candidat → **Matrice de non-régression LAB**
7. `DRAFT-CASE-LAB-T07` — Spécifier PR, revue indépendante, dispositions de merge et rollback → **Contrat PR et décision de fusion**
8. `DRAFT-CASE-LAB-T08` — Définir réconciliation de HEAD, release et retour au flux gouverné → **Dossier de livraison LAB et handoff**
