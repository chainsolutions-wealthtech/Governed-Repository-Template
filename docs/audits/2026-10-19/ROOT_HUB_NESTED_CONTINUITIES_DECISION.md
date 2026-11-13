# HUB racine — décision d'architecture en cours de nomination

**Date de consignation : 2026-10-19 (heure exacte non attestée dans GitHub avant commit)**  
**Source : instructions successives du propriétaire dans la conversation courante, résumées ici ; transcription exhaustive non disponible dans le dépôt.**  
**Statut : PROPOSED / PENDING_OWNER_CANONICAL_NAME**  
**Périmètre : chainsolutions-wealthtech/Governed-Repository-Template**  
**Fil de travail : PR #339 (DRAFT), aucun changement runtime ni main.**

## 1. Instruction propriétaire — grande poupée / HUB

L'objet principal n'est **pas** l'audit. Construire un **grand HUB canonique permanent**, initialement un espace de travail et un registre logique presque vides, prenant `main` comme **référence externe à inventorier** et non comme copie, remplacement, nouvelle autorité ou branche principale. Le HUB accueille des sous-espaces imbriqués (« poupées russes »), des missions successives et des LAB, avec liens parent/enfant et résolution ascendante et descendante. Toute nouvelle conversation doit pouvoir citer un nom ou identifiant et retrouver l'espace, son historique, ses descendants et son dernier checkpoint, sous réserve des capacités réelles d'authentification et d'intégration.

L'alias existant `GRT-AUDIT-STABILISATION` et `GRT-CONT-AUDIT-STABILISATION-20261019-001` désignent **une continuité de mission initiale / candidate**, pas le HUB racine définitif. Ne pas les promouvoir silencieusement au rang de racine. **Nom et ID racine définitifs à choisir avec le propriétaire.**

## 2. Deux branches logiques distinctes, reliées par un pont

- **Volet admission / pool** : GSCC → GSE → GACR et étapes gouvernées associées ; identités, sessions, registres, décisions et permissions selon les autorités existantes. Respecter le processus réel sans bypass.
- **Volet gouvernance / construction** : après les étapes requises, espace expérimental, analyse du code, missions, LAB, agents, prototypes, comparaison avec main. Registre propre de travaux et preuves.
- **Pont** : corrélations attestées entre objets des deux volets, sans fusion des identités ni des registres d'autorité et sans modifications majeures à la gouvernance actuelle.
- **Porte B** : entrée propriétaire GitHub authentifiée explicite, indépendante ; peut participer au HUB, mais n'acquiert pas de First Touch, GACR claim, session GACR ou F1 fictifs.

## 3. Matrice conceptuelle d'identités

```text
HUB-ROOT (identifiant définitif à décider)
├── POOL-GSCC-GSE-GACR (référence aux registres existants)
│   ├── agent logique attesté
│   ├── session attestée
│   └── événement / décision / preuve
├── GOUVERNANCE-EXPERIMENTALE
│   ├── missions
│   │   ├── AUDIT-HISTORIQUE (mission initiale)
│   │   ├── RECONSTITUTION-CODE (mission future possible, non lancée)
│   │   └── autres missions créées sur instruction
│   ├── LAB / sous-LAB (uniquement après création vérifiée)
│   ├── agents / sessions / tâches
│   └── analyses et artefacts
└── ANNUAIRE ET JOURNAL TRANSVERSAL
    ├── identifiants / alias / liens parent-enfant
    ├── instruction → décision → exécution → preuve → checkpoint
    ├── PR / issues / commits / fichiers / commentaires / Actions
    └── liens de corrélation entre les deux volets
```

La relation parent-enfant ne vaut pas attribution de rôle, identité runtime ou autorisation d'exécution. L'ID de conversation ne peut être garanti si la plateforme ne l'expose pas. Un rattachement est **attesté** seulement avec preuve d'identité/permission, objet de session créé ou résolu par mécanisme autorisé, et enregistrement durable.

## 4. Journal de mandats exprimés — synthèse fidèle, non transcription

- **M-001** : inventorier et analyser toutes les PR, issues, commentaires, commits et modifications de code depuis l'origine jusqu'au dernier état ; distinguer inventaire et lecture individuelle vérifiée.
- **M-002** : constituer un espace permanent, avec mémoire, annuaire, missions et sous-espaces nommés.
- **M-003** : créer un résolveur de continuité et routeur de fonctions nommées, réutilisant les composants existants ; tester des reprises inter-conversations attestées, sans inventer de permissions.
- **M-004** : séparer pool GSCC/GSE/GACR et gouvernance expérimentale, chacun avec registres, reliés par un pont minimal.
- **M-005** : disposer d'un grand LAB et de sous-LAB pour analyser, expérimenter et rapprocher progressivement l'existant de main, sans modifier main prématurément.
- **M-006** : historiser les instructions du propriétaire, réponses, actions, décisions, erreurs et preuves, en conservant le statut et la provenance ; **le mécanisme automatique de capture exhaustive n'est pas encore opérationnel**.
- **M-007** : définir maintenant une identité **définitive du HUB racine**, distincte de l'alias de la mission d'audit.

## 5. Critères de reprise

Un agent connecté doit pouvoir produire : nom du HUB, ID, arbre des enfants, missions et statuts, annuaire, dernier checkpoint, état des deux volets, preuves GitHub et prochaine instruction attendue. Les inconnues doivent être signalées ; aucune affirmation de mémoire exhaustive de toutes les conversations tant que l'export ou la capture n'existe pas.

**Prochaine décision propriétaire : nom canonique et identifiant permanent du HUB racine.** Aucune création de LAB, d'agent runtime, de registre d'autorité, de PR supplémentaire ou modification de main n'est autorisée par ce document.
