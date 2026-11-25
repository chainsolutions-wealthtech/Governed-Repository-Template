# Contrat de réalisation — rattachement de session et routeur de fonctions nommées

**Mandat propriétaire reçu le 2026-10-19** · `MISSION-CONTINUITE-002` · `GRT-CONT-AUDIT-STABILISATION-20261019-001` · PR #339. **Statut : spécification à implémenter, NON OPÉRATIONNELLE.**

## Besoin et résultat attendu

Toute nouvelle conversation disposant d'un client/outil compatible doit pouvoir demander `REJOINDRE GRT-AUDIT-STABILISATION`, résoudre la même mémoire et le même annuaire, puis obtenir une attestation de rattachement à une session existante ou à une nouvelle session authentifiée. Les commandes par nom doivent résoudre une fonction canonique, afficher les paramètres requis et n'exécuter que les fonctions permises par les autorités réelles.

**Aucun système ne peut détecter de lui-même chaque nouvelle conversation ChatGPT sans événement, ID ou intégration fournie par son client.** La garantie réalisable est : *chaque demande explicite de rattachement via un client compatible reçoit une preuve vérifiable ou un refus motivé*.

## Entrée et attestation

`REQUEST(space_alias, requested_entry, external_conversation_ref?, authenticated_actor_proof?, idempotency_key)`
→ résoudre espace et alias sans ambiguïté
→ relire HEAD et autorités live
→ sélectionner explicitement Porte B ou suivre Porte A
→ authentifier GitHub/acteur réel et droits effectifs
→ vérifier éventuel lien session GACR existant (sans usurper)
→ attacher si autorisé par le mécanisme existant, sinon ouvrir un **enregistrement de liaison documentaire externe** clairement distinct de la session GACR
→ émettre un reçu attestant les faits vérifiés et les limites.

Le reçu cible contient : `space_id`, `attachment_id`, `session_id` (null si absent), `agent_id` (null si absent), `entry_gate`, `actor_proof_source`, `permissions_observed`, `conversation_ref_source`, `head_sha`, `checkpoint_ref`, `issued_at_utc`, `status`, `evidence_refs`. Ne pas déclarer `VERIFIED` si l'acteur, le HEAD ou la source de conversation ne sont pas prouvés. Ne pas stocker de secrets. Clé d'idempotence pour éviter de multiplier les sessions au même reconnect.

## Fonctions nommées — catalogue initial

| Alias appelable | Fonction logique | Lecture / écriture | Gate |
|---|---|---|---|
| `ANNUAIRE` | Résoudre missions, agents, sessions, LAB, outils, événements, états | lecture | accès dépôt |
| `ETAT ESPACE` | Résoudre continuité, HEAD, checkpoint, travaux ouverts | lecture | accès dépôt |
| `MISSION AUDIT` | Lire et reprendre `MISSION-AUDIT-001` | lecture puis action mandatée | gate de l'action |
| `MISSION CONTINUITE` | Lire et reprendre `MISSION-CONTINUITE-002` | lecture puis action mandatée | gate de l'action |
| `REJOINDRE SESSION` | Résoudre et attester le rattachement | écriture de reçu éventuelle | identité/permissions vérifiées |
| `MES DROITS` | Observer les permissions natives du connecteur | lecture | authentification |
| `CREER LAB` | Invoquer le workflow LAB existant, si actif | écriture | owner/agent autorisé + workflow réel |
| `CREER AGENT` | Proposer ou déclencher l'admission selon GACR | potentielle écriture | contrôles GSCC/GSE/GACR |
| `CREER MISSION` | Ajouter une mission versionnée à l'annuaire | écriture | Porte B ou autorisation A |
| `CHECKPOINT` | Consigner les preuves et l'état de reprise | écriture | mandat et droits réels |

Les alias sont des **commandes à implémenter**, non des outils déjà installés dans ChatGPT. Ne pas confondre découverte de fonction, planification et exécution. Le routeur doit produire `UNKNOWN_FUNCTION`, `AMBIGUOUS_ALIAS`, `UNAVAILABLE_TOOL` ou `DENIED` explicitement.

## Réutilisation obligatoire

- `00_DIRECT_OWNER_ENTRY.md` et `scripts/repository_entry_router.py` pour Porte B ; jamais de permission déduite du nom.
- `00_GSCC_ENTRY.md`, GSCC/GSE/GACR/F1 pour Porte A.
- `docs/GACR_AGENT_CONTINUITY_RELAY.md`, `scripts/gacr_continuity_bus.py`, `scripts/gacr_continuity_coordination.py` et registres de sessions/continuités existants.
- `00_LAB_ENTRY.md` pour LAB ; ne pas déclarer actif un workflow simplement parce que son fichier existe.
- `CANONICAL_MISSION_DIRECTORY.md` pour la découverte des missions, sans créer de queue GACR parallèle.

## Phases d'implémentation et preuves

1. **Audit des interfaces** : schémas réels, fonctions GACR, règles d'entrée, existence du workflow LAB et permissions ; matrice de réutilisation et conflits.
2. **Résolveur read-only** : espace → alias → annuaire → dernier checkpoint ; tests collisions, noms inconnus, HEAD changeant.
3. **Routeur de fonctions** : registre de commandes, résolution déterministe, paramètres typés, dry-run, contrôles d'accès ; tests inconnues/ambiguës/permissions refusées.
4. **Rattachement attesté** : liaison documentée ou session GACR réellement admise, idempotence, preuve d'acteur, external ref optionnelle, refus explicites.
5. **Tests inter-conversations** : deux clients authentifiés, reprise stable, distinction de sessions, persistance, absence de duplications, tests refus sans authentification.
6. **Intégration gouvernée** : CI, PR #339 seulement si son périmètre est autorisé ; toute activation runtime ou modification d'autorité nécessite revue/approbation distincte.

## Invariants

- `space_id` ≠ `session_id` ≠ `agent_id` ≠ `actor_github`.
- Un alias de fonction n'est pas un grant ; un reçu de liaison n'est pas une admission GACR.
- Pas de nouveau bus, moteur de tâches, second registre d'autorité, branche ou PR parallèle.
- Pas d'écriture dans `main`, d'activation de workflow ni de merge par ce document.
- Chaque instruction et action doit être reliée à `MISSION-CONTINUITE-002`, à une preuve et à un checkpoint.
