# GRT — DOSSIER MAÎTRE DE CONSTRUCTION (projection de planification)
> Date : 2026-10-16 · dépôt : `chainsolutions-wealthtech/Governed-Repository-Template` · HEAD observé : `638fcc51c77f2454990f239b8b8cca78bac8075b`

**Mandat** : organiser et détailler les pièces à construire. Ne modifier ni P0 ni le code, ni les registres GitHub actuels. Ce paquet est une projection documentaire candidate, pas un nouvel état canonique.

## 1. Architecture des parcours

`P0 ENTRÉE EXISTANTE (intouchable)` → `P1 CONNAISSANCE / PROGRAMME` → `P2 REGISTRES / DÉPENDANCES` → `P3 LOTS ATTRIBUABLES` → `P4 PREUVES / LIVRAISONS / REPRISE`.

P0 continue d’être gouverné exclusivement par les autorités actuelles. Le paquet ne crée ni First Touch, ni agent, ni session, ni claim, ni lease.

## 2. Inventaire du découpage

- 354 fiches individuelles dans `lots/`.
- Dont 19 lots GMC historiques, 174 tâches GMC existantes et 85 artefacts GMC prévus (tous `NOT_YET_PRODUCED` dans le blueprint source).
- Chantiers de programme conservés : ARCH-001..010, IDN-001..013, RTE-001..013, CAP-001..012, SAA-001..015.
- Quatre cas structurants : CREATE, ADOPT, MAP, LAB; pas de cinquième cas pour CONTINUE_GOVERNED_WORK.
- 8 pièces de spécification candidates uniquement locales, nécessitant arbitrage et rattachement aux travaux canoniques.
- 16 enveloppes de sprint candidates, **non datées**, qui ne valent pas release et ne permettent aucun saut de dépendance.

## 3. Ordre chronologique et conditions de passage

1. **ST01 Programme Global** : issue #288, contrat directeur à valider. La planification détaillée n’est pas autorité de validation de ST01.
2. **GMC-G01..G19** : matrice modèle/cas, identités, registres, états, gates, preuves, implémentation, dépendances, comparaisons, matérialisation, quatre cas, validation générale.
3. **RTE / ARCH** : travaux compatibles avec le graphe canonique, parallélisables seulement quand dépendances distinctes et sans collisions.
4. **CAP-001..012** : après GMC-19 + RTE-012 + ARCH-006 + IDN-006 acceptés; livraison de la capsule.
5. **Cas ADOPT/MAP/LAB** : industrialisation avec leur propre baseline/test, sans confondre planification et preuve LIVE.
6. **SAA-001..015** : contrat produit, API/services, cockpit, sécurité, packaging, staging, production et livraison complète après les gates documentés.

## 4. Identifiants et registres

Chaque fiche réutilise son ID canonique lorsqu’il existe. Les identifiants nouveaux `DRAFT-*` et `SPR-DRAFT-*` sont des **références locales non canoniques**, en attente de décision. Aucun registre ne peut créer lui-même une session GACR ni une autorité.

Un objet logique peut avoir plusieurs liens de filiation : parent de construction, exigence, livrable consommé, sprint, dépendance, preuve, agent/session observée. Conserver les liens typés et leurs provenances ; ne jamais déduire un lien canonique d’une simple proximité de noms.

## 5. Contrat d’une pièce

Chaque fiche renseigne objectif, frontière, état de source, parent, dépendances, exigences candidates, instructions ordonnées, livrables, acceptation, preuves, HOLD, point de reprise et renvoi à la source canonique. Toutes les fiches comportent un `plan_file` dans `registres/pieces.json`.

## 6. Mode d’emploi pour un agent autorisé

Après son admission **sur le P0 existant** : (a) lire cette projection et les autorités réelles ; (b) sélectionner un ID déjà canonique ; (c) lire `lots/<ID>.md` ; (d) recharger le registre et le HEAD LIVE ; (e) vérifier le graphe READY/claim/collision/autorité ; (f) agir uniquement sur mandat gouverné ; (g) enregistrer événements, preuves et handoff ; (h) réconcilier les liens proposés avant toute promotion canonique.

## 7. Lacunes à ne pas masquer

- Aucun « cahier des charges global validé » à prétendre tant que ST01 #288 reste non accepté.
- Aucune attribution de sprint/calendrier sans capacité et arbitrage réel.
- Mapping `RQ-xx → lot` proposé dans ce paquet ; validation canonique encore à faire.
- Aucun `DONE` automatique sur un livrable par clôture de sprint ou achèvement d’une tâche.
- Existence d’un artefact prévu ≠ artefact produit/validé.
- Les 47 consommateurs textuels futurs d’artefacts GMC ne sont pas des IDs vérifiés de livrables : la normalisation devra s’appuyer sur GMC-G13/G16/G19.

## 8. Fichiers

- `registres/pieces.json` : toutes les pièces et leurs contrats.
- `registres/relations.json` : graphe de liens typés, sources de relation.
- `registres/exigences.json` : les 35 exigences et leurs liens candidats.
- `registres/sprints_proposes.json` : enveloppes de sprint, sans durées fictives.
- `registres/meta.json` : origine et frontière canonique.
- `registres/historique_canonique.json` : identifiants de travaux clôturés (jamais à redispatcher).
- `registres/alias_gmc.json` : mapping entre GMC-01..19 et GMC-G01..G19, sans duplication.
- `04_INDEX_TOUTES_PIECES.md` : index navigable de chaque fiche.
- `registres/controle_couverture_132_travaux.json` : couverture exhaustive des 132 IDs du registre global, sans duplication des 19 alias GMC.
- `lots/*.md` : une fiche autonome par pièce.
- `modeles/evenement_statut.json` et `modeles/handoff.json` : exemples non exécutables de preuve et reprise.
- `CONTROLES_QUALITE.json` : validation automatique du paquet.

## 9. Sources
- [docs/control-plane/CANONICAL_ARCHITECTURE.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/CANONICAL_ARCHITECTURE.md)
- [docs/control-plane/MASTER_SYSTEM_MAP.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/MASTER_SYSTEM_MAP.md)
- [docs/control-plane/REQUIREMENTS_ROADMAP.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/REQUIREMENTS_ROADMAP.md)
- [docs/control-plane/PROGRAM.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/PROGRAM.md)
- [docs/control-plane/TASKS.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/TASKS.md)
- [docs/control-plane/SAAS_PLATFORM_PROGRAM.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/SAAS_PLATFORM_PROGRAM.md)
- [docs/control-plane/GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md)
- [.governance/control-plane-state/governance-model-execution-blueprint.json](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/.governance/control-plane-state/governance-model-execution-blueprint.json)
- [.governance/control-plane-state/namespace-work-registry.json](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/.governance/control-plane-state/namespace-work-registry.json)
- [Programme Global — issue #288](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/288)
