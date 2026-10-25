# Avant-projet du contrat directeur du Programme Global — ST01

> **NON VALIDÉ — PROPOSITION DOCUMENTAIRE — SANS AUTORITÉ D'EXÉCUTION.** Cette version réutilise le mandat historique #288 et l'avant-projet #292 (commentaire 6116050125) ; elle ne prétend pas remplacer l'agent CONTRACT, GENESIS ou leur état. `ST02` demeure verrouillée jusqu'à validation explicite du contrat par l'autorité compétente.

## Section 1 — Finalité

Concevoir une plateforme de création et d'exploitation de dépôts gouvernés où chaque travail conserve une identité stable, une provenance, des droits et une continuité. Distinguer conception, exécution et preuve. Permettre une reprise gouvernée sans copier les identités d'agents ni dupliquer les travaux.

**Acceptation candidate** : vision explicite, objectifs de succès mesurables, non-confusion GRT / MCP et P0 préservé.

## Section 2 — Produit final attendu

Une plateforme utilisable avec contrôle d'entrée réutilisable, modèle canonique, programmes et tâches reliés, gestion claims/autorités, quatre cas, routeur, capsule, API versionnée, cockpit complet, projection dérivée, CI/CD, déploiement sûr, preuves et mémoire de reprise.

**Acceptation candidate** : couverture des 35 RQ, backlog CAP/RTE/ARCH/IDN/SAA, acceptance E2E ; toute absence explicitée.

## Section 3 — Périmètre

Inclus : GRT comme framework produit, source/control plane, clients Gouvern/Ekyc uniquement comme preuves existantes des cas déjà testés, registre des identités de travail, tâches, livrables, statuts, dépendances, attestations, versioning et déploiement cible.

Exclus de ce mandat : modification du parcours P0, copie/merge du projet `Patricked-code/MCP`, production immédiate, émission fictive de GACR, réutilisation des sessions d'autres agents, deuxième base canonique, changement serveur sans autorité.

**Acceptation candidate** : boundaries source/client/services clairement signées.

## Section 4 — Capacités fonctionnelles

Identité/corrélation ; gouvernance des permissions ; modèles partagés ; registres et graphe de dépendances ; planification de sprints ; dispatch gouverné ; contrats de tâches ; contrôle des versions ; revue indépendante ; audit et preuve ; reprise exacte ; comparateur de cas ; API/backend ; cockpit ; déploiement/rollback.

**Acceptation candidate** : chaque capacité a au moins un owner canonique, une exigence, un livrable et une suite de contrôle.

## Section 5 — Contraintes et invariants

Pas de changement automatique de privilège par rôle, login ou sprint. Aucun statut DONE par simple déclaration. Autorités persistées versionnées, historique append/supersede, provenance, références résolues, exact-HEAD pour mutations, anti-collision claims, gates fail-closed, secrets protégés, isolation des tenants, compatible CASE1, pas de seconde source de vérité.

**Acceptation candidate** : matrice de tests négatifs et de non-régression acceptée.

## Section 6 — Critères globaux d'acceptation

1. Une tâche définie retrouve son parent, ses exigences et ses preuves, sans identifiant orphelin.
2. Un agent reconnu peut charger un lot prêt et sa première action non vérifiée via identité/session réelles.
3. Un agent non autorisé ne peut ni prendre une tâche mutable ni court-circuiter gate/claim/CI/PR.
4. Une tâche partiellement exécutée est reprise par un autre agent autorisé sans replay d'actions prouvées.
5. Chaque livrable accepté possède contrat, provenance, vérification et handoff ; états de sprint indépendants.
6. CREATE/ADOPT/MAP/LAB réutilisent le même modèle ; MAP reste read-only, ADOPT additif, LAB isolé.
7. Capsule autonome et second fournisseur/second dépôt vérifiés avant release CAP.
8. API/UI/DB ne redéfinissent pas les règles ; vérification de parité et sécurité.
9. Staging, prod, restore et rollback sont reproductibles et attestés avant release SaaS.
10. Le système est capable de lister les éléments `PLANNED`, `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE` dans leurs machines d'état réelles, sans forcer des transitions non validées.

**Acceptation candidate** : preuve précise et gate PASS par critère, pas de conclusion à partir de cette seule proposition.

## Section 7 — Autorités réutilisées

- `CP-ARCH-001` architecture ; `CP-GOVMODEL-001` modèle commun ; `CP-NAMESPACE-001` namespaces ; `CP-SAAS-001` plateforme cible ; `docs/control-plane/PROGRAM.md`, `TASKS.md`, `NEXT_ACTION.md`, `DATA_MODEL.md`, `REQUIREMENTS_ROADMAP.md` ; P0 existant ; `.governance/control-plane-state/governance-model-execution-blueprint.json`.
- Issue Programme Global #288 et dossier CONTRACT #292, commentaire documentaire préexistant, sans transformer ces sources en décision d'approbation.

**Acceptation candidate** : tableau de précédence des autorités, signatures d'arbitrage et preuve de validation ST01 enregistrés ; seulement alors ST02 peut être considérée.

## Portes et arbitrages encore ouverts

- Valider la formulation des critères ci-dessus au titre du contrat ST01.
- Définir les tolérances NFR chiffrées (RPO/RTO, SLA/SLO, rétention, quotas, performance, temps de reprise) après acquisition de données et arbitrage propriétaire ; **aucune valeur inventée**.
- Rattacher les livrables `DEL-DRAFT-*` et la conception des sprints aux namespaces autorisés sans doubler les registres du modèle GMC.
- Déterminer clairement qui valide le contrat, les lots et les releases selon les autorités gouvernées effectives.

**État de sortie ST01** : `PRE_DRAFT_READY_FOR_GOVERNED_CONTRACT_REVIEW`, **pas** `APPROVED`, **pas** `READY_TO_EXECUTE`.
