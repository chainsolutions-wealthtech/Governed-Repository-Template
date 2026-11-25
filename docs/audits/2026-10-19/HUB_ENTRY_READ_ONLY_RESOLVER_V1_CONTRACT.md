# HUB expérimental — contrat d'entrée et résolveur lecture seule V1

**Décision propriétaire :** accueil complet automatiquement **avant** toute question sur l'action suivante. Référence native : PR #339, commentaire #6278775811. **Statut : DESIGN_ONLY / NOT_IMPLEMENTED.**

## 1. Frontière et identité
- Dépôt source : `chainsolutions-wealthtech/Governed-Repository-Template` ; `main` demeure l'autorité existante, jamais un espace de travail du HUB.
- HUB : espace expérimental distinct, sans autorité GitHub/GACR implicite. `hub_id = null` tant que le propriétaire n'a pas adopté l'identifiant immuable ; `display_name = "HUB expérimental GRT" (provisoire)`.
- Les alias `Rejoins mon HUB`, `Rejoins <hub_id>`, `Reprends la mission d'audit du HUB`, `Rejoins le LAB du HUB` sont des intentions de résolution, **pas des commandes actuellement installées**.
- Lien cible (pas encore une relation canonique attestée) : HUB → `GRT-CONT-AUDIT-STABILISATION-20261019-001` → PR #339 → commentaire #6278258031. Ne pas promouvoir l'ID de continuité au rang d'ID HUB.

## 2. Sources réutilisées (sans second registre d'autorité)
1. `00_GSCC_ENTRY.md` : Porte A ; `00_DIRECT_OWNER_ENTRY.md` : Porte B explicite, authentifiée ; `scripts/repository_entry_router.py` : sélection réelle.
2. `00_START_HERE.md` : lecture des autorités après validation de la porte choisie.
3. `SESSION_ATTACHMENT_AND_NAMED_FUNCTION_ROUTER_CONTRACT.md` : reçu de liaison, idempotence, statut de réalisation.
4. `CANONICAL_MISSION_DIRECTORY.md`, `CONTINUITIES_AND_IDENTITIES.md`, `PR339_WORKSPACE_CANONICAL_MEMORY_BOUNDARY.md` : annuaire et limites de preuve.
5. `00_LAB_ENTRY.md` et registres GACR existants : LAB, agents et sessions ; aucun LAB ni GACR créé par une lecture.

## 3. Contrat du résolveur READ_ONLY (à implémenter)
Entrée : `{repository, requested_alias_or_id, requested_entry_file?, requested_view?, external_conversation_ref?}`.

Étapes :
1. Vérifier le dépôt et l'alias/ID par correspondance déterministe exacte ; ambiguïté = `AMBIGUOUS_ALIAS`, inconnu = `UNKNOWN_SPACE` ; identité permanente absente = `HUB_ID_PENDING`, jamais synthétiser un UUID.
2. Observer les SHA HEAD de `main` et de la branche documentaire concernée, horodater la lecture et identifier les références natives.
3. Ne pas déduire une authentification d'un prompt. Pour toute opération privilégiée, sélectionner explicitement Porte A ou Porte B et contrôler l'identité/les permissions GitHub. Une lecture d'annuaire seule ne vaut pas admission.
4. Résoudre références attestées des continuités, missions, décisions, agents, sessions, LAB, branches, PR, CI et checkpoints ; séparer `VERIFIED`, `DOCUMENTARY`, `PROPOSED`, `UNKNOWN`, `STALE`.
5. Rendre l'accueil complet sans mutation. Ne demander « Que souhaitez-vous faire ? » qu'après l'accueil.

Sortie minimale : `{hub_id:null|string,hub_aliases:[],hub_status,repository,main_head_sha,workspace_head_sha,observed_at_utc,entry_gate,actor_proof_status,permissions_observed,checkpoint_ref,continuities:[],missions:[],agents:[],sessions:[],labs:[],branches:[],prs:[],ci:[],decisions:[],blockers:[],next_actions:[],evidence_refs:[],warnings:[]}`.

## 4. Ordre obligatoire de l'accueil
1. Identité HUB / état / portée ; 2. acteur et permissions réellement observés ; 3. checkpoint et décisions ; 4. continuités et missions ; 5. agents et sessions ; 6. LAB et travaux (branches/PR/CI) ; 7. blocages, limites et prochaines actions ; 8. **ensuite seulement** question au propriétaire.

## 5. Tests d'acceptation à préparer
- Alias et ID résolvent le même objet après adoption d'un ID ; nom renommé ne change pas l'ID.
- Alias inconnu, ambigu, collision avec un autre espace : échec fermé ; aucune création.
- HEAD change entre deux lectures : statut `STALE` ou nouvelle observation, pas d'état présenté comme actuel sans preuve.
- Visiteur sans authentification : aucune permission ni session prétendue.
- Session GACR absente : `session_id=null`, jamais une identité inventée.
- Double demande identique : aucun nouvel objet par simple résolution ; futur rattachement à tester séparément avec clé d'idempotence.
- Deux conversations compatibles : même annuaire et mêmes checkpoints ; `external_conversation_ref` seulement si réellement exposée.
- LAB absent : afficher `NOT_CREATED`, ne pas lancer de workflow.

## 6. Phasage et garde-fous
Cette PR #339 demeure `DRAFT / DOCUMENTATION_ONLY / NO_RUNTIME_CHANGE / NO_NEW_ISSUE / NO_MAIN_WRITE / NO_AUTO_MERGE / OWNER_REVIEW_REQUIRED`. Ce fichier est une **spécification**, pas un script de résolveur exécuté ni une preuve de reprise inter-conversations. Une implémentation Python et ses tests exigeront un périmètre de code explicitement autorisé, des vérifications anti-régression et une revue distincte avant activation.

**Prochaine action unique :** valider le schéma d'identité HUB et la table de résolution des alias sans imposer aujourd'hui un nom/ID définitif ; ensuite implémenter et tester le résolveur lecture seule dans un périmètre autorisé.
