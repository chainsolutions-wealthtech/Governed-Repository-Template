# Ratification documentaire — identité racine du HUB et mémoire des échanges

**Consigné le 2026-10-20** · **Statut : identité documentaire ratifiée pour le travail, activation runtime non attestée** · **Dépôt :** `chainsolutions-wealthtech/Governed-Repository-Template` · **PR unique :** #339 (DRAFT).

## Identité de reprise

- **Nom canonique du grand espace :** `GRT-CANONICAL-HUB`.
- **Identifiant racine documentaire permanent :** `GRT-HUB-001` (réutilise l'identifiant déjà présent dans `HUB_CANONICAL_ROOT_IDENTITY_AND_OWNER_MANDATE.md` ; ne crée pas un second HUB).
- **Mission enfant n° 1 :** `GRT-AUDIT-STABILISATION`, continuité documentaire `GRT-CONT-AUDIT-STABILISATION-20261019-001`.
- **Référence source :** branche documentaire de PR #339 et dossier `docs/audits/2026-10-19/`.
- **Source externe observée :** `main` du même dépôt ; le HUB n'est ni une copie de `main`, ni une branche, ni un nouvel espace d'autorité.

**Instruction de reprise** : « Rejoins `GRT-CANONICAL-HUB` (`GRT-HUB-001`) dans `chainsolutions-wealthtech/Governed-Repository-Template`, charge l'annuaire et le dernier checkpoint vérifiés ; pour la mission audit, rejoins `GRT-AUDIT-STABILISATION`. Ne confonds pas identité documentaire et session/permission runtime. »

## Organisation initiale

1. **Domaine admission/pool** : `GSCC → GSE → GACR`, registres et sessions propres, gates inchangés.
2. **Domaine gouvernance/expérimentation** : compréhension historique de `main`, missions, analyses, LAB/sous-LAB futurs et code isolé, registre distinct.
3. **Pont** : liens attestés entre les deux domaines, sans équivalence d'identité ni modification des autorités.
4. **Annuaire** : index des missions, agents, sessions, LAB, tâches, décisions, preuves et checkpoints. Aucun objet fictif ne doit apparaître comme actif.
5. **Journal** : chaque instruction, réponse opérationnelle, décision, action, échec et résultat doit être enregistré sous son identifiant et avec lien de preuve. Pour le présent échange, ce fichier constitue une **synthèse attestée par le commit GitHub**, pas une transcription mot à mot de toute la conversation.

## Journal initial des exigences exprimées

- `HUB-REQ-001` — espace racine permanent, initialement minimal, évoluant progressivement par sous-espaces et missions.
- `HUB-REQ-002` — deux domaines indépendants (admission GACR et gouvernance), chacun avec registre, liés par pont contrôlé.
- `HUB-REQ-003` — grand LAB isolé et sous-LAB futurs ; étudier `main` sans le modifier prématurément.
- `HUB-REQ-004` — audit historique exhaustif, **individuel** de toutes PR, issues, commentaires, commits, actions et diffs ; indexation seule insuffisante.
- `HUB-REQ-005` — identité, sessions, rattachement inter-conversations et routeur de fonctions nommées, à construire et tester réellement.
- `HUB-REQ-006` — mémoire canonique et annuaire avec liens instruction → mission → décision → action → preuve → checkpoint.
- `HUB-REQ-007` — choisir maintenant l'identité définitive du HUB, distincte de la mission d'audit ; réutiliser `GRT-HUB-001` pour éviter les collisions documentaires.
- `HUB-REQ-008` — préserver les réponses et traces : **capture automatique exhaustive non disponible** ; chaque échange doit faire l'objet d'une consignation explicite, et les conversations anciennes ne peuvent être déclarées intégralement archivées.

## Statut véridique et conditions de validation

L'identité `GRT-HUB-001` et son nom `GRT-CANONICAL-HUB` sont désormais la **référence documentaire de travail**. Les documents antérieurs marqués `PENDING_OWNER_CANONICAL_NAME` reflètent leur état historique et ne sont pas effacés. L'inscription dans un registre machine et l'activation d'un résolveur restent soumises à vérification des collisions, tests, authentification et gouvernance existante. Aucune session GACR, agent, LAB ou permission n'est créée par cette ratification.

**Prochain checkpoint :** vérifier les index et registres existants, résoudre les contradictions documentaires par références datées, construire la matrice de liens, puis développer et tester le résolveur/routeur sans modifier `main` ni créer de PR/issue concurrente.
