# Mandat de revue indépendante — LAB GRT reconstruction

**Portée** : dépôt `chainsolutions-wealthtech/Governed-Repository-Template`, issue #340, PR DRAFT #341, branche `lab/grt-reconstruction-20261020`, continuité `GRT-CONT-LAB-GRT_RECONSTRUCTION_20261020`.

## Identité et indépendance
- Le réviseur doit être une identité GitHub authentifiée, distincte de l'auteur de la PR `Wealthtechinnovations`, avec permissions vérifiées sur le dépôt.
- Aucun nom de réviseur, agent GACR, session, claim, approbation ou délégation ne peut être inventé.
- Cette demande documentaire ne vaut ni affectation d'un agent ni approbation indépendante.

## Contrôles obligatoires
1. Relire le diff complet de la PR #341 sur son **HEAD au moment de la revue**, et les entrées de gouvernance `00_DIRECT_OWNER_ENTRY.md`, `00_LAB_ENTRY.md` et la source de vérité actuelle.
2. Confirmer la filiation entre PR #339 (source documentaire non fusionnée), issue #340, PR #341, REGISTRY.json, POOL.json, QUEUE.json, LAB.md et les checkpoints.
3. Vérifier que les quatre slots sont VACANT, sans identités ou sessions concurrentes, et que les 11 tâches proposées restent non libérées, sans claims ni leases.
4. Relire les registres GACR canoniques à leur révision actuelle : ne pas inférer une admission depuis une projection dérivée ou le compte GitHub.
5. Vérifier la CI du dernier HEAD (Governance CI, GSCC Observable Arrival Gateway, GSCC Function Exposure Gate) ; relancer l'observation si le HEAD change.
6. Vérifier l'absence de mutation de main, de promotion de la queue, de merge ou de déploiement ; tester les scénarios négatifs (doublon de continuité, session fictive, claims non autorisés, branche concurrente).
7. Publier une revue GitHub explicite et sourcée (APPROVE ou REQUEST_CHANGES selon preuves), distincte de la présente rédaction.

## Critères d'admission
- CI SUCCESS sur HEAD final, revue indépendante explicite et autorisée, source GACR authentique, absence de collision et décision de gouvernance vérifiable.
- Toute lacune maintient `HOLD_AGENT_ACTIVATION` et la PR DRAFT ; aucune fusion automatique.

## État initial du mandat
`AWAITING_VERIFIED_INDEPENDENT_REVIEWER` — document préparatoire, **pas** une revue indépendante.
