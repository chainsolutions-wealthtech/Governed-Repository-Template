# Mode opératoire — Comment un agent récupère et restitue une pièce

> **Préalable absolu** : aucun agent n'entre par ce dossier. Son entrée est contrôlée exclusivement par le parcours canonique `00_GSCC_ENTRY.md` → GSCC → GSE → GACR → Q12 → F1 → RELEASE → `00_START_HERE.md`. L'identité de la pièce est indépendante de l'ID agent et de la session.

## Contrat de lecture minimal

1. L'agent s'authentifie/admet avec sa propre session. S'il est déjà reconnu, il corrèle son arrivée sans dupliquer First Touch.
2. Il lit la projection source **actualisée**, le `NEXT_ACTION`, le registre de tâches et le `HEAD` réel.
3. Il cherche une **identité canonique préexistante** par ID exact. Les `DRAFT-*` ne sont jamais dispatchables par simple lecture.
4. Il ouvre `lots/<ID>.md` et recoupe la fiche avec les sources : scope, sous-travaux, dépendances, preuves, statut, version.
5. Il confirme : rôle ≠ autorité ; Q12/F1/claim/lease et collision-domain ne sont pas présumés.
6. Il obtient l'offre/claim existant si la gouvernance du dépôt le permet. Sans claim ni autorité : lecture uniquement.
7. Il lit le dernier handoff, identifie les étapes terminées et la **première instruction non attestée**.
8. Il produit les artefacts dans la zone autorisée, avec contrôles exact-HEAD, tests et preuve ; une PR n'autorise jamais automatiquement une fusion.
9. Un vérificateur indépendant contrôle les conditions PASS/HOLD et la couverture des critères d'acceptation.
10. Il met à jour les autorités et registres existants par le mécanisme de mutation accordé ; aucun fichier de projection locale ne devient vérité de référence.
11. Il laisse un checkpoint + un handoff portant le même `work_id`, les preuves, l'état et l'action suivante.
12. Le dispatcher réévalue les tâches aval uniquement sur les sorties acceptées et libère le claim selon le modèle de concurrence.

## Fiche remise à l'agent

```text
work_id               = ID canonique vérifié, jamais ID candidat
canonical_source      = fichier/révision/code/issue autoritatif
current_head          = HEAD observé au moment de l'exécution
parent_work_id        = ID du programme / lot parent
depends_on            = objets + preuve de leur validation
output_contract       = résultat attendu, format, version, destinataire
entry_inputs          = autorité, documents, modèles et preuves consommés
instruction_steps     = ordre exact et critères de contrôle
acceptance_criteria   = conditions vérifiables PASS/HOLD
allowed_mutations      = capacités réellement accordées et autorisées
test_matrix           = unité, intégration, sécurité, non-régression si applicable
execution_agent       = ID réel et session réellement observés
evidence_refs         = liens vers preuves réelles et fraîches
handoff_ref           = checkpoint et première action non attestée
```

## Exemple de reprise

`GMC-G01-T01` reste identifiable même si l'agent A perd sa connexion. Le superviseur cherche le dernier événement et handoff valides, vérifie les outputs et les claims, puis peut proposer à l'agent B une reprise du **même** ID. Il ne doit jamais copier la session de A ou déclarer artificiellement sa tâche `DONE`.

## Réponse de sécurité

- Aucun ID valide ou ambigu → `HOLD_FOR_REVIEW`.
- HEAD modifié ou preuve périmée → revalidation et reprise contrôlée, pas de réécriture silencieuse.
- Dépendance incomplète → `BLOCKED` ou état canonique équivalent.
- Conflit de claims → refus de seconde affectation sur domaine incompatible.
- Validation échouée → conserver preuve d'échec et retour vers première étape impactée.
