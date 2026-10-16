# 00_DIRECT_OWNER_ENTRY — Porte B, entrée directe GitHub authentifiée

> **Porte B explicite, indépendante de GSCC/GSE/GACR/F1.** Ce document ne donne aucun droit nouveau et ne remplace pas `00_GSCC_ENTRY.md`. Porte A reste la voie par défaut.

## Quand utiliser cette porte

Uniquement lorsqu'une instruction demande **explicitement** : « Entre par `00_DIRECT_OWNER_ENTRY.md` ». Un simple « je viens coder » sans sélection de ce fichier ne suffit pas. Aucun First Touch ni session GACR ne sont créés dans cette porte.

```text
ARRIVÉE
→ SÉLECTION EXPLICITE : 00_DIRECT_OWNER_ENTRY.md
→ AUTHENTIFICATION RÉELLE GITHUB
→ DÉCLARATION DE RÔLE / INTENT
→ CONTRÔLE DES PERMISSIONS NATIVES ET DU HEAD
→ OPÉRATIONS GITHUB DIRECTES (sous protections/règles/CI)
```

## Vérification réelle, jamais seulement textuelle

Le connecteur GitHub authentifié doit retourner le **login effectif**, et GitHub doit exposer les **permissions effectives sur le dépôt**. Compte propriétaire autorisé uniquement si **login authentifié** égal à `Wealthtechinnovations` ou `Patricked-code` ; les autres identités sont refusées pour ce parcours privilégié.

En environnement CLI/CI avec identifiant GitHub OAuth/PAT disponible : `python3 scripts/repository_entry_router.py --entry-file 00_DIRECT_OWNER_ENTRY.md --mission "JE VIENS CODER"`. Le routeur interroge avec le credential de l'appelant `GET /user`, `GET /repos/chainsolutions-wealthtech/Governed-Repository-Template`, `GET /repos/.../commits/<default_branch>`. Il ne prend **jamais** un login libre, `GITHUB_ACTOR`, une session GACR, un nom dans le prompt ni un pseudo jeton d'autorité comme preuve. Si aucune credential n'est exposée au runtime CLI, le routeur refuse ; il ne fabrique pas de permission.

Dans une conversation ChatGPT, utiliser directement les outils GitHub connectés pour observer le login authentifié, les permissions natives du dépôt et son HEAD ; le routeur synthétise la décision de la même façon. **Ne jamais annoncer "DIRECT_OWNER_VERIFIED" sans ces preuves**. Si les permissions ne sont pas renvoyées par GitHub, ne pas les deviner : expliquer la limite et employer les contrôles GitHub réellement disponibles.

Un acteur peut déclarer librement son rôle **sans revendication d'autorité par ce rôle** :

| Déclaration exacte | Rôle | `connection_intent` |
| --- | --- | --- |
| JE VIENS CODER | CODE_AGENT | CODE_CHANGE |
| JE VIENS SUPERVISER | SUPERVISOR | OBSERVE |
| JE VIENS FAIRE UN INTAKE | INTAKER | INFORMATION_INTAKE |
| JE VIENS VÉRIFIER | REVIEWER | REVIEW |
| JE VIENS PLANIFIER | PLANNER_AGENT | CONTEXT_INTAKE |

Les anciennes politiques `.governance/connection-intent-policy.json` et `.governance/entry-action-policy.json` restent inchangées et continuent de gouverner **la porte A**. Ces labels historiques orientent le travail de la porte B mais ne font pas émerger un claim ou une permission.

## Capacités effectives

Avec `permissions.pull=true`, lecture/analyse/revue et intakes GitHub sont possibles. Avec `permissions.push=true` et dans les limites réellement imposées par GitHub, il est possible d'utiliser les fonctions GitHub directes pour créer une branche, produire des commits, modifier/supprimer des fichiers, ouvrir une PR, créer une branche `lab/*` et corriger `main`. Les protections de branche/rulesets, checks, required reviews et l'absence de force-push restent impératifs. `may_attempt_direct_main_write` **ne vaut pas preuve** qu'un push sur main sera accepté : seul le résultat GitHub atteste l'opération. Pour chaque écriture, réobserver le HEAD ou utiliser des gardes optimistes `sha` / `expected_head_sha`. En cas de conflit, arrêter et rebase/reconcile, jamais forcer.

La mission peut être spontanée : **pas de Task Queue GACR, claim, lease, F1 ni work-item préattribué systématiquement requis pour cette porte**. Une PR ou un commit constitue une trace GitHub native ; pour un nouveau LAB ou programme indépendant, consigner l'objectif, les responsables, le HEAD, les critères de clôture et les PR/issues. Un contributeur direct peut référencer une continuité GACR existante en tant que **contributeur externe**, sans prendre l'identité/session d'un participant ni créer un faux `CLIENT_EMITTER`. Tout appel à un mécanisme GACR restant gouverné doit respecter ses propres règles : la porte B ne crée pas de permis GACR.

## Commandes de sélection

Porte A (défaut, inchangée) :

```bash
python3 scripts/repository_entry_router.py
# entrée sélectionnée = 00_GSCC_ENTRY.md
```

Porte B (authentification GitHub réelle, permissions GitHub natives) :

```bash
GH_TOKEN=... python3 scripts/repository_entry_router.py \
  --entry-file 00_DIRECT_OWNER_ENTRY.md \
  --mission "JE VIENS CODER"
```

**Ne jamais afficher ou enregistrer `GH_TOKEN`.** Dans ChatGPT, ne saisissez aucun secret : utilisez exclusivement le connecteur GitHub authentifié.

## Zéro régression

L'entrée par défaut reste `00_GSCC_ENTRY.md`, avec `GSCC → GSE → GACR → Q1–Q12 → F1 → RELEASE`. Les sessions, claims, receipts, historiques, handoffs, tests et politiques existants ne sont ni supprimés ni modifiés par l'entrée B. Les tests d'acceptation A–G sont exécutés par `scripts/test_direct_owner_entry.py` et intégrés à Governance CI.

Pour accéder aux instructions communes du dépôt après **validation de la porte B**, lire `00_START_HERE.md` et les autorités du Control Plane en tenant compte de cette exception explicitement documentée. En cas de refus de la porte B, il n'y a **aucun repli silencieux avec permission** : rester bloqué ou emprunter distinctement la porte A.
