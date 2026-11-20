# STD-GITHUB-DOC-GOV-001 — Contrat transversal de gouvernance documentaire (candidat)

> Statut : PROPOSED / NOT DEPLOYED. Portée : dépôts GitHub explicitement autorisés. Cette spécification ne remplace pas CP-ARCH-001, CP-GOVMODEL-001, les règles d'entrée GRT ni les autorités de chaque dépôt.
> Travail : GRGS-CUG-DOC-GOV ; rattachement : GMC-G01 (classification préalable), CUG (distribution future), GRT (bootstrap futur), UAES (consommation future).
> Baseline GRT : main@c4950825bbba5b5212ecc7aa805647a1cbb7c8c3 (2026-11-20, observation GitHub).

## Intention et frontière

Gouverner la découverte, l'identité, le rattachement, la traçabilité et la diffusion des documents des projets/sous-projets/chantiers sans modifier automatiquement les fichiers ni répliquer une seconde source de vérité. **MODEL** : règles et schémas ; **APPLICATION_STRATEGY** : adoption GRT/CUG ; **RUNTIME_EXECUTION** : collecte, propositions, validations et preuves ; **PROJECTION** : index/cockpit. Les quatre dimensions restent séparées conformément à GMC-G01.

## Contrat documentaire

1. Identifiant stable de projet, sous-projet ou chantier, enregistré dans l'index canonique du dépôt ; identité documentaire distincte de son chemin.
2. Pour les nouveaux documents métier : `<ENTITY_ID>__<DOCUMENT_TYPE>.md`. Les fichiers conventionnels utilisés par les outils (`README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTINUITY.md`, etc.) sont des exceptions explicites, jamais renommées automatiquement.
3. Champs minimaux proposés : `document_id`, `entity_id`, `parent_entity_id` (nullable), `document_type`, `canonical_path`, `authority_ref`, `status`, `source_commit`, `schema_version`. Ne pas imposer de frontmatter incompatible : registre sidecar autorisé.
4. Une seule autorité courante par fait ; les autres documents sont des références, projections ou historiques datés.
5. Suivi, mémoire, intentions, décisions, roadmap, tâches, preuves et checkpoints isolés par périmètre ; les parents indexent les enfants sans fusion de journaux.
6. Toute modification : inventaire → classification → analyse des consommateurs → proposition → autorisation GitHub → CI/revue selon règles → preuve commit → réconciliation. Aucun push forcé ni réécriture d'historique.
7. Les événements webhook et collectes périodiques se dédupliquent par `repository_id`, `event_id`, `object_id`, `sha` ; les commentaires sont indexés par ID/date/URL sans contenu brut.
8. Les preuves de commit, PR fusionnée, CI verte, déploiement GitHub et observation runtime sont distinctes ; `UNAVAILABLE` ou `UNVERIFIED` ne devient jamais `PASS`.

## Distribution CUG proposée (non implémentée par ce document)

- `DISCOVER` : inventorier installations, dépôts, branches et permissions réellement accessibles.
- `CLASSIFY` : détecter identité des projets, sous-projets, chantiers, fichiers et exceptions.
- `RECONCILE` : comparer les versions des règles et les autorités existantes, produire un rapport d'écarts.
- `PROPOSE` : produire des changements minimaux non destructifs sur branche autorisée, sans mutation implicite.
- `VALIDATE` : contrôles statiques, tests, règles GitHub et revues exigées.
- `ATTEST` : enregistrer SHA, URL, statut CI, approbations et, séparément, état runtime si observé.

## Gates et jalons

- G0 : réconcilier cette proposition avec CP-GOVMODEL-001, GMC-G01 et les autorités existantes ; ne pas annoncer de norme active.
- G1 : vérifier sur GitHub les contrats et codes CUG existants (webhook, collecteur, GitRegistry), leurs SHA, tests et permissions ; identifier la surface d'intégration sans duplication.
- G2 : produire schéma versionné, validateur en mode rapport et tests de compatibilité sur dépôt pilote.
- G3 : ajouter le support CUG de détection/rapport, puis de propositions de mise en conformité sous autorisation explicite ; aucune écriture multi-dépôts par défaut.
- G4 : pilote GRT/UAES autorisé avec preuves CI, protections et absence de régression.
- G5 : déploiement gouverné, observation runtime séparée, extension progressive aux installations autorisées.

## État des preuves et limites

- Vérifié : GRT `00_DIRECT_OWNER_ENTRY.md`, `AGENTS.md`, `docs/control-plane/MASTER_SYSTEM_MAP.md`, `REQUIREMENTS_ROADMAP.md`, `NEXT_ACTION.md`, `GOVERNANCE_MODEL_EXECUTION_BLUEPRINT.md` ; identité GitHub `Wealthtechinnovations`, permission `admin`, HEAD main ci-dessus.
- Non vérifié dans cette passe : HEAD et code CUG actuel, installations et permissions CUG, compatibilité du validateur, CI de cette branche, état des serveurs, couverture de tous les dépôts.
- Aucun droit supplémentaire ni changement de phase GMC n'est accordé par cette proposition. Le `NEXT_ACTION` canonique demeure `GMC_01_SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES` jusqu'à validation explicite de ses gates.

## Modèle documentaire hiérarchique et pilotage Loop Engineering (candidat)

- **Grand projet** : identifiant stable, inventaire des dépôts composants, architecture, roadmap consolidée, décisions transversales et index des sous-projets ; aucune copie des mémoires enfants.
- **Projet** : autorité de contexte, SUIVI, intentions, décisions, architecture, roadmap, TODO/TASKS, preuves, continuité ; références explicites aux documents du grand projet.
- **Sous-projet / composant** : identité et dépendances, contrats, architecture locale, tâches et suivi propres ; héritage explicite des politiques parentes, sans fusion d'autorité.
- **Chantier / workblock** : objectif d'origine et ses évolutions chronologiques, propriétaire, périmètre de collision, prérequis, SHA/PR, validations, NEXT_ACTION et point de reprise.
- **Document** : registre `document_id`, `entity_id`, `parent_entity_id`, `authority_ref`, `canonical_path`, `source_commit`, `status` et version de schéma. Un document absent est `MISSING` et ne peut être déclaré rempli sur la seule existence d'un modèle.

**Ordre de travail proposé pour Loop Engineering / Open Engineering à qualifier** : réception de l'intention → lecture des autorités → inventaire et preuves → classification projet/chantier → cartographie → architecture actuelle/cible → roadmap → décomposition des tâches et dépendances → attribution bornée à l'agent codeur → tests/CI/revue → fusion gouvernée → déploiement gouverné → attestation → mémoire et reprise. Les agents observent et proposent ; aucun moteur autonome ni permission ne résulte de ce texte. La documentation est actualisée par PR sur son autorité existante, jamais par écriture multi-dépôts implicite.

**Déploiement MCP** : la stratégie GRT ne remplace pas `Patricked-code/MCP/.github/workflows/mcp-deploy.yml`. Si l'autodeploy main est activé, la fusion autorisée peut déclencher le déploiement via OIDC après CI main ; ne pas doubler le job par un déclenchement manuel concurrent. L'attestation GitHub, S1, image et runtime doit être rapprochée sur le SHA exact.
