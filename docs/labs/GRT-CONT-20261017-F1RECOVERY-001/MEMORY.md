# MÉMOIRE CANONIQUE DU LAB — GRT-CONT-20261017-F1RECOVERY-001

> **Portée : ce LAB uniquement.** Cette mémoire est l'index de vérité **de notre travail dans la branche LAB**, pas une autorité globale sur le Control Plane de `main`. Les commits GitHub et les checkpoints de l'issue #331 assurent la reprise ; aucun registre historique n'est remplacé.

## Identité et reprise

- **Continuité de développement** : `GRT-CONT-20261017-F1RECOVERY-001`.
- **Dépôt** : `chainsolutions-wealthtech/Governed-Repository-Template`.
- **Branche** : `lab/f1-recovery-isolation-20261017`.
- **Issue chronologique** : [#331](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/331).
- **PR associée** : [#332](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/332), **DRAFT / NON FUSIONNÉE**.
- **Parent documentaire** : `GRT-CONT-20261016-F1QUEUE-001`, issue #327, PR #328 (déjà fusionnée).
- **Acteur GitHub attesté** : `Wealthtechinnovations`. **Aucun ID de session ChatGPT ou GACR ne peut être supposé**.
- **BASE** : `main@b3d7f623b443be6b0fe987dd2c527a6a4d4a53d0`.
- **LAB avant ce registre** : `6ba31d9930a477afcd7d2d4885e2eff7fe13af92`.

## Hiérarchie canonique et workflow comme source de preuves

**ID principal de mémoire** : `GRT-LABMEM-20261017-F1RECOVERY-001`. **ID de continuité de développement** : `GRT-CONT-20261017-F1RECOVERY-001`. Ces deux identifiants sont différents et reliés.

- `MEMORY_IDENTITY.json` : racine mémoire et sous-ID typés `OBS`, `EVID`, `EVT`, `DEC`, `INSTR`, `TEST`, `HYP`, `GAP`, `PROB`, `REQ`, `ANL`, `TASK`, `CLAIM`, `CHK`, etc. Les 27 premiers ID historiques sont conservés et mappés, pas renommés.
- `OWNER_INSTRUCTIONS.json` : demande d'origine et son niveau de provenance ; une retranscription dans l'issue #331 ne vaut pas signature du propriétaire dans GitHub.
- `WORKFLOW_EVIDENCE.json` : quatre exécutions GitHub Actions, chacune avec **ID de run, commit exact, noms des jobs, contrôles lancés, conclusions, contrôles ignorés et échecs éventuels**, et liens vers des observations. Les listes exhaustives des étapes sont dans le registre.
- Une **CI verte** est une preuve que les contrôles exécutés ont réussi ; elle ne prouve pas le fonctionnement E2E ni la correction automatique de risques déjà identifiés (notamment D03 et D04 du dispatcher).
- Lorsqu'un nouveau workflow termine, conserver son `run_id`, SHA, source, étapes réellement exécutées et résultats, erreurs, limites et `observation_id` ou `task_id` associé. La preuve ne remplace ni une analyse ni une décision.

**Chaîne d'interprétation et de préparation :**
`ORIGINE (instruction ou problème) → OBSERVATION → PREUVE (code, test, CI) → ENRICHISSEMENT DE LA MÉMOIRE → ANALYSE DES ÉCARTS → COMPRÉHENSION DES BESOINS / PROBLÈMES → PRÉPARATION CHRONOLOGIQUE DES TÂCHES`.

Le **registre des tâches** et le futur **module de claims hiérarchiques** sont des éléments du squelette à décrire dans l'ordre indiqué par le propriétaire. **Ils ne sont pas interdits.** Les exécutions des tâches viennent plus tard ; la présente mise à jour ne distribue aucune tâche et ne prend aucun claim.

### Reconstitution à partir du seul ID de continuité

La lecture de `GRT-CONT-20261017-F1RECOVERY-001` doit permettre de retrouver : les problèmes initiaux de récupération F1 et changement HEAD, l'alias facultatif d'agent, l'analyse du dispatcher GACR et de ses risques, les instructions de construction de la mémoire LAB, les IDs parent/enfants, la chronologie, les exigences de registre des tâches et de claims hiérarchiques, et les résultats des workflows.

**Statut documentaire** : 9 observations techniques initiales ; 12 événements chronologiques ; 6 décisions ou qualifications ; 6 candidats d'analyse historiques non affectés. Ce ne sont pas des nombres figés.

## Identité vérifiée de la continuité et du LAB

Le registre [`LAB_IDENTITY_AND_RELEASES.json`](./LAB_IDENTITY_AND_RELEASES.json) conserve **cinq champs distincts** : commit testé (avec runs et résultats), branche LAB, commit de fusion réel ou nul, ID du pool d'agents attesté ou nul, et continuité préservée. Les valeurs manquantes ne sont pas inventées.

- Commit vert observé avant l'enregistrement : `a8f6368d927eb1420a6f6c1378201954d354d31f` ; quatre workflows success, mais E2E live non prouvé.
- Branche : `lab/f1-recovery-isolation-20261017`.
- PR #332 DRAFT et non fusionnée : **aucun commit de fusion réel**. Un SHA de fusion potentielle ne vaut pas fusion.
- ID du pool d'agents de ce LAB : **non attesté**. `AGENT_CAPACITY_POOL` désigne un modèle, pas l'identifiant d'un pool réservé au LAB.
- Continuité `GRT-CONT-20261017-F1RECOVERY-001`, liée à la mémoire `GRT-LABMEM-20261017-F1RECOVERY-001`.

## Nouvelle exigence propriétaire — pool minimal LAB relié à GACR

Le propriétaire impose que **tout pool minimal dédié à ce LAB**, lorsqu'il existera, ait **son propre ID**, **lié à une identité GACR canonique vérifiée** et à toutes les relations pertinentes (agents, sessions, rôles, capacités, F1 et admission quand applicable, traces, tâches, offres, claims, preuves). Ce lien doit être reconstituable chronologiquement, avec une provenance pour chaque transition.

- Sous-ID d'exigence : `GRT-LABMEM-20261017-F1RECOVERY-001-REQ-001`.
- Sous-ID de relation requise : `GRT-LABMEM-20261017-F1RECOVERY-001-REL-001`.
- Registre : [`POOL_GACR_LINK_REQUIREMENT.json`](./POOL_GACR_LINK_REQUIREMENT.json).
- Source : [instruction transcrite dans l'issue #331](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/331#issuecomment-6227560349).
- **État vérifié :** ID du pool LAB = non établi ; référence GACR précise = non établie. Ne pas utiliser à tort un pool `AGENT_CAPACITY_POOL` projeté ou une continuité historique étrangère.
- Ceci est une **condition de conception du squelette**, pas un claim ni une affectation créée aujourd'hui. Les étapes de réalisation seront indiquées ultérieurement par le propriétaire.

## Sources canoniques du LAB

| Registre | Rôle | Règle |
| --- | --- | --- |
| `OBSERVATIONS.json` | Faits observés, preuves et limites | Une nouvelle observation reçoit un nouvel ID ; jamais transformer une hypothèse en preuve en silence |
| `CHRONOLOGY.json` | Événements ordonnés, commits, commentaires et tests | Ajout chronologique, provenance des événements et pas de dates inventées |
| `DECISIONS.json` | Choix du propriétaire, politiques préservées, décisions en attente | `PENDING` n'est pas une autorisation |
| `TASK_CANDIDATES.json` | Hypothèses de travaux à analyser, sans dispatch | **Pas** une Task Queue : aucun claim ni affectation |
| `CHECKPOINT.json` | Dernier HEAD observé, prochain acte et preuve CI disponible | Snapshot révisable, Git et issue constituent l'historique |
| `MEMORY_IDENTITY.json` | Racine LAB et sous-ID typés | Conservation des anciens identifiants |
| `OWNER_INSTRUCTIONS.json` | Origines et demandes du propriétaire | Retenues sans fabriquer de signature GitHub |
| `WORKFLOW_EVIDENCE.json` | Runs/commits/contrôles/résultats GitHub Actions | Preuves liées aux observations et tâches futures |
| `MEMORY.md` | Mode d'emploi/reprise, résumé et limitations | Une nouvelle conversation doit lire les fichiers machine et le dernier commentaire d'issue |

## Chaîne de construction obligatoire

`OBSERVATION → PREUVE → INSCRIPTION CHRONOLOGIQUE → ANALYSE → VALIDATION DE DÉCISION → CANDIDAT DE TÂCHE → PROMOTION GOUVERNÉE (SEULEMENT SI AUTORISÉE) → EXÉCUTION → TESTS → CHECKPOINT`.

À chaque intervention, lire HEAD main et LAB, issue/PR, puis append les **nouveaux éléments confirmés**, ajouter des hypothèses sans les présenter comme établies et mettre à jour le checkpoint et la prochaine action. L'acte de planifier ne doit pas créer une session, un claim, un verrou ni une seconde queue.

## État de connaissance enregistré

- **F1** : correction de reprise et conservation de preuves dans PR #332, CI simulée réussie, **E2E live non prouvé**.
- **Agent sans nom** : champ alias facultatif testé en simulation, identité GSCC réelle préservée.
- **Dispatcher GACR** : audit D01–D08 dans [rapport spécifique](../GRT-CONT-20261017-F1RECOVERY-001_DISPATCHER_AUDIT.md) ; D03 provenance F1 et D04 revalidation d'offre sont des **risques ouverts**.
- **Registre préexistant** : 9 observations techniques sourcées ; 12 événements ordonnés ; 6 décisions/qualifications ; 6 candidats **non distribués**.
- **Dernier cycle CI avant mémoire** : [Governance CI #38983239494](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/actions/runs/38983239494) et trois contrôles GSCC success ; ce sont des tests de LAB, pas des validations de fusion ou de sécurité E2E.

## Anti-régression et limites

1. Lire les sources réelles, n'écrire que sur `lab/f1-recovery-isolation-20261017` et observer le HEAD avant chaque mutation ; refuser une mise à jour si la branche a bougé.
2. Un verdict de simulation qui reproduit une faille signifie **risque confirmé localement**, non **défaut corrigé**.
3. Une admission F1 propriétaire, un slot de pool, un lien d'identités ou une offre GACR ne confèrent pas des droits GitHub natifs.
4. Les travaux sans autorisation restent des candidats d'analyse. Ne pas modifier la queue canonique ni `GMC-01`.
5. Documenter l'inconnu : ID de session, limites d'E2E, preuves absentes et état des hypothèses.
6. La liaison technique identité de session ↔ continuité de développement ↔ GSCC/GSE/GACR reste **différée** jusqu'au mandat propre du propriétaire.

## Reprise universelle

Depuis une nouvelle conversation GitHub connectée, demander :

```text
Rejoins GRT-CONT-20261017-F1RECOVERY-001.
Lis l'issue #331, la PR #332 et les fichiers
docs/labs/GRT-CONT-20261017-F1RECOVERY-001/{MEMORY.md,MEMORY_IDENTITY.json,OWNER_INSTRUCTIONS.json,WORKFLOW_EVIDENCE.json,OBSERVATIONS.json,CHRONOLOGY.json,DECISIONS.json,TASK_CANDIDATES.json,CHECKPOINT.json}.
Reobserve main et LAB HEAD. Reprends le dernier checkpoint et enrichis la mémoire
avant tout nouveau plan ou code, sans usurper une session.
```

La mémoire évolue **au rythme des interventions enregistrées**. Elle ne se complète pas en arrière-plan lorsqu'aucun agent ne travaille.
