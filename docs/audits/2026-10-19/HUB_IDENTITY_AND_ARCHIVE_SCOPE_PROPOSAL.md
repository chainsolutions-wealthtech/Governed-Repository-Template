# Identité du hub racine et périmètre d'archivage — proposition du propriétaire

**État : PROPOSED, NON ACTIVÉ** · 2026-10-20 · PR #339 · dépôt exclusif `chainsolutions-wealthtech/Governed-Repository-Template`.

## Distinction racine / mission / référentiel

- **Hub racine proposé** : `GRT-CANONICAL-HUB`, identifiant documentaire proposé `GRT-HUB-001`. Ce sont des noms **candidats**, pas une nouvelle autorité runtime, une nouvelle branche `main` ni une entrée existante du registre GACR.
- **Référence du système existant** : `main` est la source historique de vérité à inventorier, analyser et éventuellement refléter dans un LAB isolé. Le hub est initialement un conteneur logique **vide de nouveaux sous-projets**, pas une copie de code déjà attestée.
- **Mission initiale** : `GRT-AUDIT-STABILISATION`, continuité documentaire proposée `GRT-CONT-AUDIT-STABILISATION-20261019-001`, PR #339. Elle est enfant du hub, non sa racine.
- **Deux domaines distincts** : (A) processus d'entrée et pool GSCC/GSE/GACR avec ses propres identités, sessions, claims, registres et autorisations ; (B) espace de gouvernance, analyse, LAB et code avec ses propres missions et artefacts. Un pont de corrélation **prouvé, sans transfert implicite de permissions**, relie les deux.

## Consignes du propriétaire à préserver

1. Donner au hub une identité durable, puis attribuer progressivement des IDs uniques à chaque mission, agent, session, LAB, sous-espace, tâche, décision, événement, communication, fichier joint et checkpoint.
2. Recevoir des instructions successives ; les archiver avec la réponse, la décision, l'état, les preuves et la prochaine action. Ne pas exécuter les phases futures avant mandat.
3. Reconstituer individuellement tout l'historique du dépôt : chaque PR, issue, commentaire, commit, action, workflow et changement de code, avec liens, dépendances et état de vérification.
4. Construire un grand LAB et des LAB enfants isolés pour tester progressivement des propositions issues de `main` ; aucune refonte ni fusion automatique de `main`.
5. Prévoir un annuaire consultable par noms et IDs, et une reprise entre conversations qui relise le dernier checkpoint et les autorités réelles.
6. Traiter les fichiers joints comme des artefacts avec origine, empreinte, version, mission et emplacement ; ne jamais affirmer leur archivage sans transfert/présence vérifiés.

## Limites factuelles d'archivage

Une conversation ChatGPT n'est **pas** automatiquement une session GACR. Un historique de conversation et ses pièces jointes ne sont **pas** automatiquement copiés dans GitHub. Les textes des messages utilisateur et des réponses peuvent être résumés dans ce mandat, mais une **transcription exhaustive mot pour mot** et l'archivage de toutes les pièces jointes exigent un mécanisme d'export/ingestion vérifié et, pour les données privées, une politique de confidentialité. Ne pas annoncer « mémoire canonique complète » tant que les événements ne sont pas tous attestés.

## Registres logiques cibles (sans doublonner les sources existantes)

`HUB_DIRECTORY` → `MISSIONS` → `INSTRUCTIONS` / `DECISIONS` / `EVENTS` / `EVIDENCE` / `ATTACHMENTS` / `CHECKPOINTS` ; liens vers `AGENTS`, `SESSIONS`, `GACR_POOL`, `LABS`, `TASKS`, `PR`, `ISSUES`, `COMMITS`, `ACTIONS`. Les index sont des vues de lecture, pas une seconde autorité de permissions.

**Prochaine décision demandée** : valider ou renommer l'identité du hub avant d'enregistrer une identité définitive. Aucun changement runtime ou de gouvernance n'est autorisé par ce document.
