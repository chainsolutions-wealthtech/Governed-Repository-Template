# CHAINFLOW / GR-000302 — réconciliation HEAD avant PREP-003

Statut: **candidat isolé, PR uniquement**. Continuité d'origine `GRT-CONT-20261014-CHAINFLOW-POC-01`, ancre [#301](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/301), demande originale [#302](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/302). Pas de nouvelle GR, queue, session GACR, claim, grant WRITE, LAB cible ou fusion de `main`.

## Anomalie démontrée

GR-000302 reste révision 12, `EXECUTING_PREPARATION/PREP-003`, avec PREP-001 et PREP-002 DONE attestés à `e20b172b149a30ec8ece77c828e3c00614078d38`. Le `main` actuel diffère. Le PREP-003 originel demande `lab/chainflow-live-poc` créée à cet ancien SHA. Il est interdit de fabriquer `created=true`, effacer l'histoire ou recréer une branche ancienne.

## Réconciliation proposée

- Entrée `/governed-reconcile-gr302 {"expected_revision":12,"expected_head":"<HEAD_main_reobservé>","reason":"..."}` sur **la même issue #302**, uniquement après fusion contrôlée d'une PR portant cette capacité.
- Le pont vérifie l'auteur de commentaire et `sender` GitHub propriétaire, l'association, la révision machine et le HEAD live ; consulte `GET /branches/lab%2Fchainflow-live-poc` et n'accepte **que HTTP 404 authentique** comme preuve d'absence.
- Préserve le plan et les preuves PREP-001/PREP-002, sans les revalider rétroactivement ; archive le plan originel dans `preparation_reconciliation_history`.
- Insère `PREP-002R` `READ_VERIFY` pour constater une nouvelle fois le HEAD et l'absence du LAB ; recale `PREP-003.required_evidence.base_head_sha` sur le nouveau HEAD observé.
- Supprime l'ancienne réponse `plan_approved` de la **projection courante** (sans effacer l'historique) et revient à `WAITING_FOR_PLAN_APPROVAL` pour une nouvelle décision explicite du propriétaire.
- La commande ne crée pas le LAB, n'exécute pas PREP-003/004 et n'accorde aucune autorisation GACR. Une nouvelle revalidation est exigée avant l'approbation et la preuve PREP-002R si le HEAD change.
- Un rejet retourne une preuve de refus, sans modifier le marqueur de la GR. L'issue GitHub n'offre pas de CAS atomique natif avec le pont actuel ; celui-ci vérifie l'état juste avant le PATCH, sans revendiquer une atomicité supérieure. Une sérialisation explicite du workflow d'issue est recommandée en production avant activation.

## NOVA — frontière stricte

L'arrivée NOVA #321 possède un RELEASE F1 historique et un rôle propriétaire CODE_AGENT limité à GR-000302/PREP-003 et PREP-004 ; **ni présence vivante, ni work offer, ni claim/lease, ni `SCOPED_GIT_WRITE`** n'en découlent. Pour une mutation ultérieure : corrélation réelle du client NOVA, disponibilité authentifiée, assignation par le GACR existant, offer → accept → claim/lease → exact HEAD/collision → grant et seulement ensuite création LAB. Ne pas toucher à `GMC-01`.

## Séquence de validation

1. CI : `python3 scripts/test_governed_gr302_reconciliation.py` et tests historiques du Control Plane.
2. Vérifier le diff et la CI sur le SHA exact de la PR.
3. Revue indépendante ; **aucune fusion de cette PR n'est donnée par le seul mandat de préparation**.
4. Après fusion explicitement approuvée, réobserver le HEAD live et utiliser la commande sur #302 sous le propriétaire authentifié ; publier les preuves/états en #302 et indexer en #301.
5. Le plan revalidé n'accordera toujours aucune autorisation WRITE à NOVA.

Provenance : intervention GitHub directe propriétaire, porte B explicitement acceptée dans la conversation, branche isolée, sans Codex ni écriture sur `main`.
