# Index de toutes les pièces de construction

> HEAD : `638fcc51c77f2454990f239b8b8cca78bac8075b` ; projection locale, sans création de nouvelle identité canonique.

Les 354 identités d’objet ci-dessous pointent sur des fiches autonomes. Les éléments P0 (admission) restent intouchés.

## architecture (1)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `CP-ARCH-001` | Architecture cible acceptée | ACCEPTED_TARGET_ARCHITECTURE | [Consulter](lots/CP-ARCH-001.md) |

## atomic_task (174)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `GMC-G01-T01` | Recenser toutes les autorités et artefacts de gouvernance connus. | PLANNED | [Consulter](lots/GMC-G01-T01.md) |
| `GMC-G01-T02` | Classifier chaque artefact/règle en MODEL, APPLICATION_STRATEGY, RUNTIME_EXECUTION, PROJECTION ou UNRESOLVED. | PLANNED | [Consulter](lots/GMC-G01-T02.md) |
| `GMC-G01-T03` | Inventorier les sémantiques communes enfermées ou dupliquées dans un seul cas. | PLANNED | [Consulter](lots/GMC-G01-T03.md) |
| `GMC-G01-T04` | Cartographier la frontière source-control-plane versus surface distribuée aux clients. | PLANNED | [Consulter](lots/GMC-G01-T04.md) |
| `GMC-G01-T05` | Séparer données de définition réutilisables et données d'exécution concrètes. | PLANNED | [Consulter](lots/GMC-G01-T05.md) |
| `GMC-G01-T06` | Identifier contradictions, chevauchements et éléments sans propriétaire canonique. | PLANNED | [Consulter](lots/GMC-G01-T06.md) |
| `GMC-G01-T07` | Produire MODEL_BOUNDARY_MATRIX avec provenance. | PLANNED | [Consulter](lots/GMC-G01-T07.md) |
| `GMC-G01-T08` | Valider la matrice contre CP-ARCH-001, CP-GOVMODEL-001 et les décisions. | PLANNED | [Consulter](lots/GMC-G01-T08.md) |
| `GMC-G02-T01` | Définir les 18 types d'entités du modèle. | PLANNED | [Consulter](lots/GMC-G02-T01.md) |
| `GMC-G02-T02` | Définir les namespaces et conventions d'IDs stables. | PLANNED | [Consulter](lots/GMC-G02-T02.md) |
| `GMC-G02-T03` | Définir les métadonnées communes obligatoires. | PLANNED | [Consulter](lots/GMC-G02-T03.md) |
| `GMC-G02-T04` | Définir les règles de références inter-registres et cardinalités. | PLANNED | [Consulter](lots/GMC-G02-T04.md) |
| `GMC-G02-T05` | Définir lifecycle, dépréciation et supersession sans suppression silencieuse. | PLANNED | [Consulter](lots/GMC-G02-T05.md) |
| `GMC-G02-T06` | Définir la version du Governance Model indépendamment du Template. | PLANNED | [Consulter](lots/GMC-G02-T06.md) |
| `GMC-G02-T07` | Définir invariants de validation: IDs uniques, références résolues, provenance, no orphan. | PLANNED | [Consulter](lots/GMC-G02-T07.md) |
| `GMC-G02-T08` | Produire des exemples minimaux valides pour chaque type. | PLANNED | [Consulter](lots/GMC-G02-T08.md) |
| `GMC-G03-T01` | Recenser les domaines explicitement documentés. | PLANNED | [Consulter](lots/GMC-G03-T01.md) |
| `GMC-G03-T02` | Découvrir les domaines implicites dans policies/schemas/scripts/workflows. | PLANNED | [Consulter](lots/GMC-G03-T02.md) |
| `GMC-G03-T03` | Découvrir les domaines révélés par SQL, runtime objects et tests. | PLANNED | [Consulter](lots/GMC-G03-T03.md) |
| `GMC-G03-T04` | Fusionner les candidats en conservant toutes les provenances. | PLANNED | [Consulter](lots/GMC-G03-T04.md) |
| `GMC-G03-T05` | Normaliser synonymes, chevauchements et granularités. | PLANNED | [Consulter](lots/GMC-G03-T05.md) |
| `GMC-G03-T06` | Définir purpose, scope, exclusions et responsabilité de chaque domaine. | PLANNED | [Consulter](lots/GMC-G03-T06.md) |
| `GMC-G03-T07` | Attribuer statut IMPLEMENTED/PARTIAL/PLANNED/FUTURE. | PLANNED | [Consulter](lots/GMC-G03-T07.md) |
| `GMC-G03-T08` | Associer les capabilities candidates sans les finaliser. | PLANNED | [Consulter](lots/GMC-G03-T08.md) |
| `GMC-G03-T09` | Contrôler qu'aucun élément majeur du modèle reste hors domaine sans justification. | PLANNED | [Consulter](lots/GMC-G03-T09.md) |
| `GMC-G04-T01` | Importer les capabilities déclarées comme candidats. | PLANNED | [Consulter](lots/GMC-G04-T01.md) |
| `GMC-G04-T02` | Découvrir les capabilities implicites à partir des comportements et tests. | PLANNED | [Consulter](lots/GMC-G04-T02.md) |
| `GMC-G04-T03` | Dédupliquer par résultat fonctionnel et non par fichier. | PLANNED | [Consulter](lots/GMC-G04-T03.md) |
| `GMC-G04-T04` | Définir purpose, inputs, outputs, préconditions, postconditions et erreurs. | PLANNED | [Consulter](lots/GMC-G04-T04.md) |
| `GMC-G04-T05` | Définir statut et applicabilité MANDATORY/OPTIONAL/CONDITIONAL/NOT_APPLICABLE. | PLANNED | [Consulter](lots/GMC-G04-T05.md) |
| `GMC-G04-T06` | Rattacher chaque capability à son domaine. | PLANNED | [Consulter](lots/GMC-G04-T06.md) |
| `GMC-G04-T07` | Identifier dépendances préliminaires entre capabilities. | PLANNED | [Consulter](lots/GMC-G04-T07.md) |
| `GMC-G04-T08` | Associer composants/implémentations/tests candidats. | PLANNED | [Consulter](lots/GMC-G04-T08.md) |
| `GMC-G04-T09` | Produire la revue de couverture et capabilities orphelines/non prouvées. | PLANNED | [Consulter](lots/GMC-G04-T09.md) |
| `GMC-G05-T01` | Décomposer chaque capability en responsabilités fonctionnelles minimales. | PLANNED | [Consulter](lots/GMC-G05-T01.md) |
| `GMC-G05-T02` | Inspecter les artefacts actuels pour identifier les composants implicitement réalisés. | PLANNED | [Consulter](lots/GMC-G05-T02.md) |
| `GMC-G05-T03` | Séparer COMPONENT et IMPLEMENTATION_ARTIFACT. | PLANNED | [Consulter](lots/GMC-G05-T03.md) |
| `GMC-G05-T04` | Définir responsabilité, interfaces et contrats. | PLANNED | [Consulter](lots/GMC-G05-T04.md) |
| `GMC-G05-T05` | Identifier composants partagés entre capabilities. | PLANNED | [Consulter](lots/GMC-G05-T05.md) |
| `GMC-G05-T06` | Détecter doublons, chevauchements et composants manquants. | PLANNED | [Consulter](lots/GMC-G05-T06.md) |
| `GMC-G05-T07` | Associer objets, contrôles, implémentations et tests candidats. | PLANNED | [Consulter](lots/GMC-G05-T07.md) |
| `GMC-G05-T08` | Vérifier que chaque capability possède une décomposition ou un gap explicite. | PLANNED | [Consulter](lots/GMC-G05-T08.md) |
| `GMC-G06-T01` | Inventorier les objets à partir des schemas, JSON et tables SQL. | PLANNED | [Consulter](lots/GMC-G06-T01.md) |
| `GMC-G06-T02` | Normaliser les objets équivalents représentés sous plusieurs formes. | PLANNED | [Consulter](lots/GMC-G06-T02.md) |
| `GMC-G06-T03` | Extraire champs, types, required/optional, valeurs permises et defaults. | PLANNED | [Consulter](lots/GMC-G06-T03.md) |
| `GMC-G06-T04` | Définir mutabilité, ownership/authority et nature canonical/derived/runtime. | PLANNED | [Consulter](lots/GMC-G06-T04.md) |
| `GMC-G06-T05` | Extraire les relations explicites et implicites. | PLANNED | [Consulter](lots/GMC-G06-T05.md) |
| `GMC-G06-T06` | Définir cardinalités et contraintes d'intégrité. | PLANNED | [Consulter](lots/GMC-G06-T06.md) |
| `GMC-G06-T07` | Conserver provenance précise vers schema/table/path/symbole. | PLANNED | [Consulter](lots/GMC-G06-T07.md) |
| `GMC-G06-T08` | Associer chaque objet aux composants/capabilities. | PLANNED | [Consulter](lots/GMC-G06-T08.md) |
| `GMC-G06-T09` | Contrôler objets/champs/relations orphelins et divergences schema-code-SQL. | PLANNED | [Consulter](lots/GMC-G06-T09.md) |
| `GMC-G07-T01` | Identifier tous les objets possédant state/status/mode/phase. | PLANNED | [Consulter](lots/GMC-G07-T01.md) |
| `GMC-G07-T02` | Extraire les valeurs déclarées par schemas et JSON. | PLANNED | [Consulter](lots/GMC-G07-T02.md) |
| `GMC-G07-T03` | Extraire les états implicites dans branches conditionnelles et tests. | PLANNED | [Consulter](lots/GMC-G07-T03.md) |
| `GMC-G07-T04` | Normaliser synonymes et distinguer état d'objet, phase et résultat de contrôle. | PLANNED | [Consulter](lots/GMC-G07-T04.md) |
| `GMC-G07-T05` | Classer initial/intermediate/terminal/error/hold/unknown. | PLANNED | [Consulter](lots/GMC-G07-T05.md) |
| `GMC-G07-T06` | Définir la sémantique exacte de chaque état. | PLANNED | [Consulter](lots/GMC-G07-T06.md) |
| `GMC-G07-T07` | Définir evidence requirements/freshness pour déclarer l'état. | PLANNED | [Consulter](lots/GMC-G07-T07.md) |
| `GMC-G07-T08` | Vérifier rattachement de chaque état à un objet et une machine cohérente. | PLANNED | [Consulter](lots/GMC-G07-T08.md) |
| `GMC-G08-T01` | Recenser transitions explicites et codées. | PLANNED | [Consulter](lots/GMC-G08-T01.md) |
| `GMC-G08-T02` | Relier chaque transition à FROM/TO state IDs. | PLANNED | [Consulter](lots/GMC-G08-T02.md) |
| `GMC-G08-T03` | Définir trigger, actor/role et authority requirements. | PLANNED | [Consulter](lots/GMC-G08-T03.md) |
| `GMC-G08-T04` | Définir préconditions, action et postconditions. | PLANNED | [Consulter](lots/GMC-G08-T04.md) |
| `GMC-G08-T05` | Associer controls, gates et evidence types requis. | PLANNED | [Consulter](lots/GMC-G08-T05.md) |
| `GMC-G08-T06` | Définir failure state et recovery/reconciliation. | PLANNED | [Consulter](lots/GMC-G08-T06.md) |
| `GMC-G08-T07` | Cataloguer transitions interdites et fail-closed. | PLANNED | [Consulter](lots/GMC-G08-T07.md) |
| `GMC-G08-T08` | Comparer documentation/code/tests et produire les gaps. | PLANNED | [Consulter](lots/GMC-G08-T08.md) |
| `GMC-G08-T09` | Inventorier et normaliser les workflows qui orchestrent les transitions et phases. | PLANNED | [Consulter](lots/GMC-G08-T09.md) |
| `GMC-G08-T10` | Construire le Failure Registry à partir des états/branches d'échec observés. | PLANNED | [Consulter](lots/GMC-G08-T10.md) |
| `GMC-G08-T11` | Construire le Recovery Registry à partir des mécanismes resume/reconcile/retry/repair. | PLANNED | [Consulter](lots/GMC-G08-T11.md) |
| `GMC-G09-T01` | Extraire les contrôles explicites des autorités et décisions. | PLANNED | [Consulter](lots/GMC-G09-T01.md) |
| `GMC-G09-T02` | Extraire les contrôles des policies JSON et schemas. | PLANNED | [Consulter](lots/GMC-G09-T02.md) |
| `GMC-G09-T03` | Extraire les guards/validations du code. | PLANNED | [Consulter](lots/GMC-G09-T03.md) |
| `GMC-G09-T04` | Extraire les contrôles de Governance CI. | PLANNED | [Consulter](lots/GMC-G09-T04.md) |
| `GMC-G09-T05` | Relier les tests existants aux contrôles. | PLANNED | [Consulter](lots/GMC-G09-T05.md) |
| `GMC-G09-T06` | Dédupliquer et normaliser avec IDs stables. | PLANNED | [Consulter](lots/GMC-G09-T06.md) |
| `GMC-G09-T07` | Définir purpose, scope, severity, trigger, PASS, FAIL et failure behavior. | PLANNED | [Consulter](lots/GMC-G09-T07.md) |
| `GMC-G09-T08` | Associer evidence types, implementation IDs et test IDs candidats. | PLANNED | [Consulter](lots/GMC-G09-T08.md) |
| `GMC-G09-T09` | Produire le rapport documented-only/implemented-only/untested/conflicting. | PLANNED | [Consulter](lots/GMC-G09-T09.md) |
| `GMC-G10-T01` | Identifier les points de décision critiques. | PLANNED | [Consulter](lots/GMC-G10-T01.md) |
| `GMC-G10-T02` | Associer à chaque gate les control IDs requis. | PLANNED | [Consulter](lots/GMC-G10-T02.md) |
| `GMC-G10-T03` | Définir logique d'agrégation et ALLOW/STOP/HOLD. | PLANNED | [Consulter](lots/GMC-G10-T03.md) |
| `GMC-G10-T04` | Définir acteur/authority et approbations éventuelles. | PLANNED | [Consulter](lots/GMC-G10-T04.md) |
| `GMC-G10-T05` | Définir evidence requirements et freshness. | PLANNED | [Consulter](lots/GMC-G10-T05.md) |
| `GMC-G10-T06` | Définir failure/hold/recovery behavior. | PLANNED | [Consulter](lots/GMC-G10-T06.md) |
| `GMC-G10-T07` | Définir dépendances et ordre entre gates. | PLANNED | [Consulter](lots/GMC-G10-T07.md) |
| `GMC-G10-T08` | Vérifier que les gates réutilisent les contrôles sans les redéfinir. | PLANNED | [Consulter](lots/GMC-G10-T08.md) |
| `GMC-G10-T09` | Consolider le Authority Registry utilisé par les gates, contrôles et transitions. | PLANNED | [Consulter](lots/GMC-G10-T09.md) |
| `GMC-G11-T01` | Inventorier les preuves concrètes déjà enregistrées. | PLANNED | [Consulter](lots/GMC-G11-T01.md) |
| `GMC-G11-T02` | Abstraire les evidence types réutilisables. | PLANNED | [Consulter](lots/GMC-G11-T02.md) |
| `GMC-G11-T03` | Définir format/schema de chaque evidence type. | PLANNED | [Consulter](lots/GMC-G11-T03.md) |
| `GMC-G11-T04` | Définir producer, subject, authority et freshness. | PLANNED | [Consulter](lots/GMC-G11-T04.md) |
| `GMC-G11-T05` | Définir invalidation/expiration. | PLANNED | [Consulter](lots/GMC-G11-T05.md) |
| `GMC-G11-T06` | Définir provenance et retention/replay. | PLANNED | [Consulter](lots/GMC-G11-T06.md) |
| `GMC-G11-T07` | Relier evidence types aux controls/transitions/gates. | PLANNED | [Consulter](lots/GMC-G11-T07.md) |
| `GMC-G11-T08` | Vérifier séparation Evidence Type vs Evidence Record. | PLANNED | [Consulter](lots/GMC-G11-T08.md) |
| `GMC-G11-T09` | Produire la couverture et les gaps de preuve. | PLANNED | [Consulter](lots/GMC-G11-T09.md) |
| `GMC-G12-T01` | Inventorier les artefacts d'implémentation. | PLANNED | [Consulter](lots/GMC-G12-T01.md) |
| `GMC-G12-T02` | Associer chaque élément modèle à ses artefacts actuels. | PLANNED | [Consulter](lots/GMC-G12-T02.md) |
| `GMC-G12-T03` | Enregistrer les relations many-to-many model↔artifact. | PLANNED | [Consulter](lots/GMC-G12-T03.md) |
| `GMC-G12-T04` | Définir type d'artefact, portée source/client, statut et version. | PLANNED | [Consulter](lots/GMC-G12-T04.md) |
| `GMC-G12-T05` | Relier chaque implémentation à ses tests/evidence producers. | PLANNED | [Consulter](lots/GMC-G12-T05.md) |
| `GMC-G12-T06` | Identifier artefacts orphelins. | PLANNED | [Consulter](lots/GMC-G12-T06.md) |
| `GMC-G12-T07` | Identifier éléments modèle sans implémentation et classer PLANNED/FUTURE/GAP. | PLANNED | [Consulter](lots/GMC-G12-T07.md) |
| `GMC-G12-T08` | Vérifier boundary source-only/distributed. | PLANNED | [Consulter](lots/GMC-G12-T08.md) |
| `GMC-G12-T09` | Produire la matrice bidirectionnelle MODEL↔IMPLEMENTATION. | PLANNED | [Consulter](lots/GMC-G12-T09.md) |
| `GMC-G12-T10` | Construire le Test Registry et relier chaque test aux éléments modèle qu'il couvre. | PLANNED | [Consulter](lots/GMC-G12-T10.md) |
| `GMC-G13-T01` | Collecter les dépendances explicites. | PLANNED | [Consulter](lots/GMC-G13-T01.md) |
| `GMC-G13-T02` | Ajouter les dépendances fonctionnelles entre model elements. | PLANNED | [Consulter](lots/GMC-G13-T02.md) |
| `GMC-G13-T03` | Classer HARD/CONDITIONAL/ORDERING/DATA/CONTROL/EVIDENCE/IMPLEMENTATION. | PLANNED | [Consulter](lots/GMC-G13-T03.md) |
| `GMC-G13-T04` | Construire le graphe orienté avec provenance par edge. | PLANNED | [Consulter](lots/GMC-G13-T04.md) |
| `GMC-G13-T05` | Détecter cycles et dépendances manquantes. | PLANNED | [Consulter](lots/GMC-G13-T05.md) |
| `GMC-G13-T06` | Calculer ordres topologiques load/install/validate/repair. | PLANNED | [Consulter](lots/GMC-G13-T06.md) |
| `GMC-G13-T07` | Identifier critical path et dépendances à fort impact. | PLANNED | [Consulter](lots/GMC-G13-T07.md) |
| `GMC-G13-T08` | Valider le graphe contre CREATE/ADOPT/MAP/LAB. | PLANNED | [Consulter](lots/GMC-G13-T08.md) |
| `GMC-G13-T09` | Définir comportements en cas de cycle/unknown. | PLANNED | [Consulter](lots/GMC-G13-T09.md) |
| `GMC-G14-T01` | Définir le modèle d'observation d'un target repository. | PLANNED | [Consulter](lots/GMC-G14-T01.md) |
| `GMC-G14-T02` | Définir les clés de matching sémantique par type. | PLANNED | [Consulter](lots/GMC-G14-T02.md) |
| `GMC-G14-T03` | Formaliser les huit classifications et conditions. | PLANNED | [Consulter](lots/GMC-G14-T03.md) |
| `GMC-G14-T04` | Formaliser les actions REUSE/MAP_REUSE/EXTEND/ADD/HOLD/MIGRATE/DISCOVER/SKIP. | PLANNED | [Consulter](lots/GMC-G14-T04.md) |
| `GMC-G14-T05` | Définir résolution quand plusieurs classifications candidates existent. | PLANNED | [Consulter](lots/GMC-G14-T05.md) |
| `GMC-G14-T06` | Définir traitement UNKNOWN et recherches supplémentaires. | PLANNED | [Consulter](lots/GMC-G14-T06.md) |
| `GMC-G14-T07` | Définir interaction applicability/dependencies. | PLANNED | [Consulter](lots/GMC-G14-T07.md) |
| `GMC-G14-T08` | Définir le schéma ComparisonResult. | PLANNED | [Consulter](lots/GMC-G14-T08.md) |
| `GMC-G14-T09` | Construire des cas d'exemple CREATE/ADOPT/MAP. | PLANNED | [Consulter](lots/GMC-G14-T09.md) |
| `GMC-G14-T10` | Formaliser l'Applicability Contract réutilisable par CREATE/ADOPT/MAP/LAB. | PLANNED | [Consulter](lots/GMC-G14-T10.md) |
| `GMC-G15-T01` | Définir matching exact, alias et équivalence sémantique des champs. | PLANNED | [Consulter](lots/GMC-G15-T01.md) |
| `GMC-G15-T02` | Définir matrice de compatibilité des types. | PLANNED | [Consulter](lots/GMC-G15-T02.md) |
| `GMC-G15-T03` | Définir règles enum exact/subset/superset/conflict. | PLANNED | [Consulter](lots/GMC-G15-T03.md) |
| `GMC-G15-T04` | Définir règles required/optional/default/nullability. | PLANNED | [Consulter](lots/GMC-G15-T04.md) |
| `GMC-G15-T05` | Définir règles cardinalité/relation compatibility. | PLANNED | [Consulter](lots/GMC-G15-T05.md) |
| `GMC-G15-T06` | Comparer contraintes, mutabilité, lifecycle et authority. | PLANNED | [Consulter](lots/GMC-G15-T06.md) |
| `GMC-G15-T07` | Définir comparaison control coverage et test coverage. | PLANNED | [Consulter](lots/GMC-G15-T07.md) |
| `GMC-G15-T08` | Définir remontée des différences fines vers PARTIAL/CONFLICT. | PLANNED | [Consulter](lots/GMC-G15-T08.md) |
| `GMC-G15-T09` | Produire des exemples de comparaison fine avec classification attendue. | PLANNED | [Consulter](lots/GMC-G15-T09.md) |
| `GMC-G16-T01` | Définir l'arborescence cible .governance/governance-model. | PLANNED | [Consulter](lots/GMC-G16-T01.md) |
| `GMC-G16-T02` | Définir docs/governance-model et règles docs générées vs autorités manuelles. | PLANNED | [Consulter](lots/GMC-G16-T02.md) |
| `GMC-G16-T03` | Définir schemas/governance-model pour chaque registre et ComparisonResult. | PLANNED | [Consulter](lots/GMC-G16-T03.md) |
| `GMC-G16-T04` | Définir format de chaque registry JSON et références inter-registres. | PLANNED | [Consulter](lots/GMC-G16-T04.md) |
| `GMC-G16-T05` | Définir manifest model_id/model_version/status/registry pointers/contracts/releases. | PLANNED | [Consulter](lots/GMC-G16-T05.md) |
| `GMC-G16-T06` | Définir le plan de migration SQL additive governance_*. | PLANNED | [Consulter](lots/GMC-G16-T06.md) |
| `GMC-G16-T07` | Définir l'extension du materializer EXISTANT sans second materializer canonique. | PLANNED | [Consulter](lots/GMC-G16-T07.md) |
| `GMC-G16-T08` | Définir versioning modèle, release manifest, provenance et supersession. | PLANNED | [Consulter](lots/GMC-G16-T08.md) |
| `GMC-G16-T09` | Définir validations CI: schemas, IDs, refs, deps, model↔SQL parity, docs generation. | PLANNED | [Consulter](lots/GMC-G16-T09.md) |
| `GMC-G16-T10` | Produire le plan d'implémentation ordonné, sans l'exécuter. | PLANNED | [Consulter](lots/GMC-G16-T10.md) |
| `GMC-G17-T01` | Identifier les entry points du Control Plane qui ont besoin du modèle. | PLANNED | [Consulter](lots/GMC-G17-T01.md) |
| `GMC-G17-T02` | Définir séquence load manifest → resolve version → load registries → validate. | PLANNED | [Consulter](lots/GMC-G17-T02.md) |
| `GMC-G17-T03` | Définir dependency/applicability resolution contract. | PLANNED | [Consulter](lots/GMC-G17-T03.md) |
| `GMC-G17-T04` | Définir fail-closed si manifest/schema/ref/dependency invalide. | PLANNED | [Consulter](lots/GMC-G17-T04.md) |
| `GMC-G17-T05` | Définir liaison model_version avec runs/sessions/evidence/comparisons. | PLANNED | [Consulter](lots/GMC-G17-T05.md) |
| `GMC-G17-T06` | Définir interfaces modèle ↔ catalogue de parcours existant. | PLANNED | [Consulter](lots/GMC-G17-T06.md) |
| `GMC-G17-T07` | Définir observabilité/evidence du chargement/validation. | PLANNED | [Consulter](lots/GMC-G17-T07.md) |
| `GMC-G17-T08` | Définir backward compatibility avec CASE 1 et clients existants. | PLANNED | [Consulter](lots/GMC-G17-T08.md) |
| `GMC-G17-T09` | Définir matrice de tests nécessaire avant activation. | PLANNED | [Consulter](lots/GMC-G17-T09.md) |
| `GMC-G18-T01` | Construire le Common Case Adapter Contract. | PLANNED | [Consulter](lots/GMC-G18-T01.md) |
| `GMC-G18-T02` | Mapper CREATE: applicability → dependency order → instantiate → validate → attest. | PLANNED | [Consulter](lots/GMC-G18-T02.md) |
| `GMC-G18-T03` | Mapper ADOPT: observe → compare → gaps/conflicts → additive integration plan → verify. | PLANNED | [Consulter](lots/GMC-G18-T03.md) |
| `GMC-G18-T04` | Mapper MAP: observe → map → compare → gaps → evidence, avec NO WRITE. | PLANNED | [Consulter](lots/GMC-G18-T04.md) |
| `GMC-G18-T05` | Mapper LAB: baseline model → candidate → model-to-model compare → regression → release. | PLANNED | [Consulter](lots/GMC-G18-T05.md) |
| `GMC-G18-T06` | Définir outputs communs et spécifiques. | PLANNED | [Consulter](lots/GMC-G18-T06.md) |
| `GMC-G18-T07` | Définir write/authority/gate policies par stratégie. | PLANNED | [Consulter](lots/GMC-G18-T07.md) |
| `GMC-G18-T08` | Définir matrice de regression sur un même model_version. | PLANNED | [Consulter](lots/GMC-G18-T08.md) |
| `GMC-G18-T09` | Définir migration du catalog.json vers consommation du modèle sans perdre l'historique. | PLANNED | [Consulter](lots/GMC-G18-T09.md) |
| `GMC-G18-T10` | Vérifier qu'aucun élément central n'est redéfini en doublon dans un cas. | PLANNED | [Consulter](lots/GMC-G18-T10.md) |
| `GMC-G19-T01` | Exécuter completeness review de tous les registries/contracts prévus. | PLANNED | [Consulter](lots/GMC-G19-T01.md) |
| `GMC-G19-T02` | Exécuter consistency review IDs/refs/dependencies/lifecycle/applicability. | PLANNED | [Consulter](lots/GMC-G19-T02.md) |
| `GMC-G19-T03` | Vérifier traçabilité source↔model↔implementation↔test/evidence. | PLANNED | [Consulter](lots/GMC-G19-T03.md) |
| `GMC-G19-T04` | Valider matrice cross-case CREATE/ADOPT/MAP/LAB. | PLANNED | [Consulter](lots/GMC-G19-T04.md) |
| `GMC-G19-T05` | Définir/valider model-to-model release diff et compatibilité. | PLANNED | [Consulter](lots/GMC-G19-T05.md) |
| `GMC-G19-T06` | Classer tous les gaps en BLOCKER/POST-1.0/FUTURE. | PLANNED | [Consulter](lots/GMC-G19-T06.md) |
| `GMC-G19-T07` | Préparer release manifest Governance Model 1.0.0 et mapping Template versions. | PLANNED | [Consulter](lots/GMC-G19-T07.md) |
| `GMC-G19-T08` | Définir attestation/evidence bundle/checkpoint/handoff/release gate. | PLANNED | [Consulter](lots/GMC-G19-T08.md) |
| `GMC-G19-T09` | N'autoriser 1.0.0 que si tous exit gates critiques PASS. | PLANNED | [Consulter](lots/GMC-G19-T09.md) |
| `GMC-G19-T10` | Préparer handoff PostgreSQL/API/Admin UI après stabilisation. | PLANNED | [Consulter](lots/GMC-G19-T10.md) |

## canonical_backlog_task (63)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `ARCH-001` | Établir CP-ARCH-001 et sa traçabilité | DONE | [Consulter](lots/ARCH-001.md) |
| `ARCH-002` | Registre des autorités et révisions | DONE | [Consulter](lots/ARCH-002.md) |
| `ARCH-003` | Matérialisation des historiques existants | DONE | [Consulter](lots/ARCH-003.md) |
| `ARCH-004` | Réducteur transversal des événements/projections | PLANNED | [Consulter](lots/ARCH-004.md) |
| `ARCH-005` | Modèle de rôles/capacités/autorités | PLANNED | [Consulter](lots/ARCH-005.md) |
| `ARCH-006` | Contrôle croisé architectures, manifest, tâches, handoffs | PLANNED | [Consulter](lots/ARCH-006.md) |
| `ARCH-007` | Document PDF dérivé du Markdown canonique | PLANNED | [Consulter](lots/ARCH-007.md) |
| `ARCH-008` | Concevoir API de gouvernance sur sémantiques validées | FUTURE | [Consulter](lots/ARCH-008.md) |
| `ARCH-009` | Concevoir projection PostgreSQL compatible | FUTURE | [Consulter](lots/ARCH-009.md) |
| `ARCH-010` | Application web Admin comme surface gouvernée | FUTURE | [Consulter](lots/ARCH-010.md) |
| `CAP-001` | Périmètre de la capsule réutilisable | PLANNED | [Consulter](lots/CAP-001.md) |
| `CAP-002` | Cartographier noyau réutilisable et couplages | PLANNED | [Consulter](lots/CAP-002.md) |
| `CAP-003` | Geler schemas/interfaces publics versionnés | PLANNED | [Consulter](lots/CAP-003.md) |
| `CAP-004` | Définir extraction compatible du noyau | PLANNED | [Consulter](lots/CAP-004.md) |
| `CAP-005` | Définir SPI adaptateurs provider/repository/persistence | PLANNED | [Consulter](lots/CAP-005.md) |
| `CAP-006` | Définir adaptateur de référence GitHub/ChatGPT | PLANNED | [Consulter](lots/CAP-006.md) |
| `CAP-007` | Définir abstraction persistence sans source concurrente | PLANNED | [Consulter](lots/CAP-007.md) |
| `CAP-008` | Définir installation/upgrade/rollback compatible | PLANNED | [Consulter](lots/CAP-008.md) |
| `CAP-009` | Matrice de régression sécurité/portabilité | PLANNED | [Consulter](lots/CAP-009.md) |
| `CAP-010` | Preuve E2E second dépôt propre | PLANNED | [Consulter](lots/CAP-010.md) |
| `CAP-011` | Preuve E2E second fournisseur/adaptateur | PLANNED | [Consulter](lots/CAP-011.md) |
| `CAP-012` | Release capsule 1.0.0 | PLANNED | [Consulter](lots/CAP-012.md) |
| `IDN-001` | Modèle identité PRINCIPAL ≠ AGENT ≠ CONNECTION ≠ SESSION | DONE | [Consulter](lots/IDN-001.md) |
| `IDN-002` | Capture de l’acteur GitHub authentifié | DONE | [Consulter](lots/IDN-002.md) |
| `IDN-003` | Registre stable des principals | DONE | [Consulter](lots/IDN-003.md) |
| `IDN-004` | Journal des événements de connexion | DONE | [Consulter](lots/IDN-004.md) |
| `IDN-005` | Règles de session et reprise | DONE | [Consulter](lots/IDN-005.md) |
| `IDN-006` | Admission / reprise de session éprouvée | DONE | [Consulter](lots/IDN-006.md) |
| `IDN-007` | Lien rôle ↔ session | DONE | [Consulter](lots/IDN-007.md) |
| `IDN-008` | Snapshot d’autorité distinct du rôle | DONE | [Consulter](lots/IDN-008.md) |
| `IDN-009` | Routage identité/session/role/intention | DONE | [Consulter](lots/IDN-009.md) |
| `IDN-010` | Persistance mémoire relationnelle des sessions | DONE | [Consulter](lots/IDN-010.md) |
| `IDN-011` | Tests création/reprise/ambiguïté | DONE | [Consulter](lots/IDN-011.md) |
| `IDN-012` | Adaptateur source du Control Plane | DONE | [Consulter](lots/IDN-012.md) |
| `IDN-013` | Projection future identité/session API/UI | FUTURE | [Consulter](lots/IDN-013.md) |
| `RTE-001` | Définir la porte WORK_ON_CONTROL_PLANE ou APPLY_GOVERNANCE_CASE | PLANNED | [Consulter](lots/RTE-001.md) |
| `RTE-002` | Définir CODE_IMPLEMENTATION / EXECUTE_EXISTING_TASK / ADD_OR_ENRICH_INFORMATION | PLANNED | [Consulter](lots/RTE-002.md) |
| `RTE-003` | Définir la sélection exacte des quatre cas, continuation hors cinquième cas | PLANNED | [Consulter](lots/RTE-003.md) |
| `RTE-004` | Concevoir le routage automatique depuis session/role/autorité | PLANNED | [Consulter](lots/RTE-004.md) |
| `RTE-005` | Auto-charger PROGRAM/TASKS/NEXT_ACTION pour Control Plane | PLANNED | [Consulter](lots/RTE-005.md) |
| `RTE-006` | Réconcilier tâche existante / information nouvelle / intake | PLANNED | [Consulter](lots/RTE-006.md) |
| `RTE-007` | Router les cas vers les questionnaires existants | PLANNED | [Consulter](lots/RTE-007.md) |
| `RTE-008` | Persister réponses, choix et événements du routage | PLANNED | [Consulter](lots/RTE-008.md) |
| `RTE-009` | Automatiser uniquement les actions déjà autorisées | PLANNED | [Consulter](lots/RTE-009.md) |
| `RTE-010` | Échouer fermé pour ambiguïté / autorité / tâche manquante | PLANNED | [Consulter](lots/RTE-010.md) |
| `RTE-011` | Définir la matrice exhaustive de tests des branches | PLANNED | [Consulter](lots/RTE-011.md) |
| `RTE-012` | Reprendre la première question non résolue sans rejouer les étapes validées | PLANNED | [Consulter](lots/RTE-012.md) |
| `RTE-013` | Préparer l’exposition future du routeur via API/UI | FUTURE | [Consulter](lots/RTE-013.md) |
| `SAA-001` | Contrat produit SaaS, tenancy, NFR et déploiement | PLANNED | [Consulter](lots/SAA-001.md) |
| `SAA-002` | Contrat REST/OpenAPI v1 versionné | PLANNED | [Consulter](lots/SAA-002.md) |
| `SAA-003` | Frontières et propriété des services backend | PLANNED | [Consulter](lots/SAA-003.md) |
| `SAA-004` | Lier authentification/RBAC aux autorités gouvernées | PLANNED | [Consulter](lots/SAA-004.md) |
| `SAA-005` | Projection PostgreSQL/migrations/reconciliation | PLANNED | [Consulter](lots/SAA-005.md) |
| `SAA-006` | API gateway, services et workers sans doublon des gates | PLANNED | [Consulter](lots/SAA-006.md) |
| `SAA-007` | Contrat UX/navigation/actions du cockpit complet | PLANNED | [Consulter](lots/SAA-007.md) |
| `SAA-008` | Surfaces de supervision du cockpit | PLANNED | [Consulter](lots/SAA-008.md) |
| `SAA-009` | Actions opérationnelles avec contrôles réels | PLANNED | [Consulter](lots/SAA-009.md) |
| `SAA-010` | Audit, observabilité et durcissement sécurité | PLANNED | [Consulter](lots/SAA-010.md) |
| `SAA-011` | Packaging déploiement reproductible | PLANNED | [Consulter](lots/SAA-011.md) |
| `SAA-012` | Staging équivalent production et E2E | PLANNED | [Consulter](lots/SAA-012.md) |
| `SAA-013` | Déploiement production gouverné | PLANNED | [Consulter](lots/SAA-013.md) |
| `SAA-014` | Recette end-to-end des quatre cas et de la continuité | PLANNED | [Consulter](lots/SAA-014.md) |
| `SAA-015` | Release SaaS 1.0.0, sauvegarde/restauration, mise à jour/rollback | PLANNED | [Consulter](lots/SAA-015.md) |

## knowledge_artifact (85)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `GMA-ACTION-MAPPING` | Action Mapping | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-ACTION-MAPPING.md) |
| `GMA-ADOPT-MODEL-BINDING` | Adopt Model Binding | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-ADOPT-MODEL-BINDING.md) |
| `GMA-APPLICABILITY-CONTRACT` | Applicability Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-APPLICABILITY-CONTRACT.md) |
| `GMA-AUTHORITY-REGISTRY` | Authority Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-AUTHORITY-REGISTRY.md) |
| `GMA-BACKWARD-COMPATIBILITY-PLAN` | Backward Compatibility Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-BACKWARD-COMPATIBILITY-PLAN.md) |
| `GMA-CAPABILITY-APPLICABILITY-CANDIDATES` | Capability Applicability Candidates | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CAPABILITY-APPLICABILITY-CANDIDATES.md) |
| `GMA-CAPABILITY-COMPONENT-MAP` | Capability Component Map | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CAPABILITY-COMPONENT-MAP.md) |
| `GMA-CAPABILITY-COVERAGE-REPORT` | Capability Coverage Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CAPABILITY-COVERAGE-REPORT.md) |
| `GMA-CAPABILITY-REGISTRY` | Capability Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CAPABILITY-REGISTRY.md) |
| `GMA-CI-VALIDATION-PLAN` | Ci Validation Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CI-VALIDATION-PLAN.md) |
| `GMA-COMMON-CASE-ADAPTER-CONTRACT` | Common Case Adapter Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMMON-CASE-ADAPTER-CONTRACT.md) |
| `GMA-COMMON-METADATA-CONTRACT` | Common Metadata Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMMON-METADATA-CONTRACT.md) |
| `GMA-COMPARISON-CLASSIFICATION-RULES` | Comparison Classification Rules | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMPARISON-CLASSIFICATION-RULES.md) |
| `GMA-COMPARISON-CONTRACT` | Comparison Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMPARISON-CONTRACT.md) |
| `GMA-COMPARISON-RESULT-MODEL` | Comparison Result Model | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMPARISON-RESULT-MODEL.md) |
| `GMA-COMPONENT-GAP-REPORT` | Component Gap Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMPONENT-GAP-REPORT.md) |
| `GMA-COMPONENT-REGISTRY` | Component Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-COMPONENT-REGISTRY.md) |
| `GMA-CONSTRAINT-COMPARISON-RULES` | Constraint Comparison Rules | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CONSTRAINT-COMPARISON-RULES.md) |
| `GMA-CONTROL-GAP-REPORT` | Control Gap Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CONTROL-GAP-REPORT.md) |
| `GMA-CONTROL-IMPLEMENTATION-TEST-MATRIX` | Control Implementation Test Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CONTROL-IMPLEMENTATION-TEST-MATRIX.md) |
| `GMA-CONTROL-PLANE-MODEL-CONSUMPTION-CONTRACT` | Control Plane Model Consumption Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CONTROL-PLANE-MODEL-CONSUMPTION-CONTRACT.md) |
| `GMA-CONTROL-PLANE-TEST-MATRIX` | Control Plane Test Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CONTROL-PLANE-TEST-MATRIX.md) |
| `GMA-CONTROL-REGISTRY` | Control Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CONTROL-REGISTRY.md) |
| `GMA-CREATE-MODEL-BINDING` | Create Model Binding | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CREATE-MODEL-BINDING.md) |
| `GMA-CROSS-CASE-REGRESSION-MATRIX` | Cross Case Regression Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CROSS-CASE-REGRESSION-MATRIX.md) |
| `GMA-CROSS-CASE-VALIDATION-REPORT` | Cross Case Validation Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-CROSS-CASE-VALIDATION-REPORT.md) |
| `GMA-DEPENDENCY-GAP-REPORT` | Dependency Gap Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-DEPENDENCY-GAP-REPORT.md) |
| `GMA-DEPENDENCY-REGISTRY` | Dependency Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-DEPENDENCY-REGISTRY.md) |
| `GMA-DOMAIN-CANDIDATE-LEDGER` | Domain Candidate Ledger | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-DOMAIN-CANDIDATE-LEDGER.md) |
| `GMA-DOMAIN-COVERAGE-REPORT` | Domain Coverage Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-DOMAIN-COVERAGE-REPORT.md) |
| `GMA-DOMAIN-REGISTRY` | Domain Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-DOMAIN-REGISTRY.md) |
| `GMA-EVIDENCE-GAP-REPORT` | Evidence Gap Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-EVIDENCE-GAP-REPORT.md) |
| `GMA-EVIDENCE-REQUIREMENT-MATRIX` | Evidence Requirement Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-EVIDENCE-REQUIREMENT-MATRIX.md) |
| `GMA-EVIDENCE-TYPE-REGISTRY` | Evidence Type Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-EVIDENCE-TYPE-REGISTRY.md) |
| `GMA-FAIL-CLOSED-RULES` | Fail Closed Rules | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FAIL-CLOSED-RULES.md) |
| `GMA-FAILURE-REGISTRY` | Failure Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FAILURE-REGISTRY.md) |
| `GMA-FIELD-COMPARISON-RULES` | Field Comparison Rules | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FIELD-COMPARISON-RULES.md) |
| `GMA-FIELD-REGISTRY` | Field Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FIELD-REGISTRY.md) |
| `GMA-FINAL-GOVERNANCE-MODEL-ASSEMBLY` | Final Governance Model Assembly | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FINAL-GOVERNANCE-MODEL-ASSEMBLY.md) |
| `GMA-FINE-GRAINED-GAP-MODEL` | Fine Grained Gap Model | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FINE-GRAINED-GAP-MODEL.md) |
| `GMA-FORBIDDEN-TRANSITION-CATALOGUE` | Forbidden Transition Catalogue | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FORBIDDEN-TRANSITION-CATALOGUE.md) |
| `GMA-FOUR-CASE-CONSUMPTION-MAP` | Four Case Consumption Map | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-FOUR-CASE-CONSUMPTION-MAP.md) |
| `GMA-GATE-CONTROL-MATRIX` | Gate Control Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GATE-CONTROL-MATRIX.md) |
| `GMA-GATE-REGISTRY` | Gate Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GATE-REGISTRY.md) |
| `GMA-GATE-SEQUENCE-MAP` | Gate Sequence Map | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GATE-SEQUENCE-MAP.md) |
| `GMA-GLOBAL-DEPENDENCY-GRAPH` | Global Dependency Graph | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GLOBAL-DEPENDENCY-GRAPH.md) |
| `GMA-GOVERNANCE-MODEL-1-0-0-RELEASE-PLAN` | Governance Model 1 0 0 Release Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GOVERNANCE-MODEL-1-0-0-RELEASE-PLAN.md) |
| `GMA-GOVERNANCE-MODEL-COMPLETENESS-REPORT` | Governance Model Completeness Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GOVERNANCE-MODEL-COMPLETENESS-REPORT.md) |
| `GMA-GOVERNANCE-MODEL-METAMODEL` | Governance Model Metamodel | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-GOVERNANCE-MODEL-METAMODEL.md) |
| `GMA-ID-NAMESPACE-CONTRACT` | Id Namespace Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-ID-NAMESPACE-CONTRACT.md) |
| `GMA-IMPLEMENTATION-REGISTRY` | Implementation Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-IMPLEMENTATION-REGISTRY.md) |
| `GMA-INSTALL-ORDER` | Install Order | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-INSTALL-ORDER.md) |
| `GMA-INTEGRATION-CONTRACT` | Integration Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-INTEGRATION-CONTRACT.md) |
| `GMA-LAB-MODEL-BINDING` | Lab Model Binding | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-LAB-MODEL-BINDING.md) |
| `GMA-MAP-MODEL-BINDING` | Map Model Binding | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MAP-MODEL-BINDING.md) |
| `GMA-MATERIALIZER-EXTENSION-PLAN` | Materializer Extension Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MATERIALIZER-EXTENSION-PLAN.md) |
| `GMA-MODEL-BOUNDARY-MATRIX` | Model Boundary Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MODEL-BOUNDARY-MATRIX.md) |
| `GMA-MODEL-CLASSIFICATION-TAXONOMY` | Model Classification Taxonomy | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MODEL-CLASSIFICATION-TAXONOMY.md) |
| `GMA-MODEL-IMPLEMENTATION-MATRIX` | Model Implementation Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MODEL-IMPLEMENTATION-MATRIX.md) |
| `GMA-MODEL-LOAD-SEQUENCE` | Model Load Sequence | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MODEL-LOAD-SEQUENCE.md) |
| `GMA-MODEL-VERSIONING-PLAN` | Model Versioning Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-MODEL-VERSIONING-PLAN.md) |
| `GMA-OBJECT-MODEL-CONSISTENCY-REPORT` | Object Model Consistency Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-OBJECT-MODEL-CONSISTENCY-REPORT.md) |
| `GMA-OBJECT-REGISTRY` | Object Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-OBJECT-REGISTRY.md) |
| `GMA-ORPHAN-ARTIFACT-REPORT` | Orphan Artifact Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-ORPHAN-ARTIFACT-REPORT.md) |
| `GMA-RECOVERY-REGISTRY` | Recovery Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-RECOVERY-REGISTRY.md) |
| `GMA-REFERENCE-AND-SUPERSESSION-RULES` | Reference And Supersession Rules | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-REFERENCE-AND-SUPERSESSION-RULES.md) |
| `GMA-REGISTRY-STORAGE-ARCHITECTURE` | Registry Storage Architecture | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-REGISTRY-STORAGE-ARCHITECTURE.md) |
| `GMA-RELATIONSHIP-REGISTRY` | Relationship Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-RELATIONSHIP-REGISTRY.md) |
| `GMA-RELEASE-CONTRACT` | Release Contract | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-RELEASE-CONTRACT.md) |
| `GMA-RELEASE-READINESS-REPORT` | Release Readiness Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-RELEASE-READINESS-REPORT.md) |
| `GMA-REPAIR-ORDER` | Repair Order | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-REPAIR-ORDER.md) |
| `GMA-SCHEMA-PLAN` | Schema Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-SCHEMA-PLAN.md) |
| `GMA-SQL-MIGRATION-PLAN` | Sql Migration Plan | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-SQL-MIGRATION-PLAN.md) |
| `GMA-STATE-MACHINE-CATALOGUE` | State Machine Catalogue | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-STATE-MACHINE-CATALOGUE.md) |
| `GMA-STATE-REGISTRY` | State Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-STATE-REGISTRY.md) |
| `GMA-STATE-SEMANTICS-REPORT` | State Semantics Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-STATE-SEMANTICS-REPORT.md) |
| `GMA-TEST-REGISTRY` | Test Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-TEST-REGISTRY.md) |
| `GMA-TRACEABILITY-MATRIX` | Traceability Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-TRACEABILITY-MATRIX.md) |
| `GMA-TRANSITION-GAP-REPORT` | Transition Gap Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-TRANSITION-GAP-REPORT.md) |
| `GMA-TRANSITION-REGISTRY` | Transition Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-TRANSITION-REGISTRY.md) |
| `GMA-TYPE-COMPATIBILITY-MATRIX` | Type Compatibility Matrix | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-TYPE-COMPATIBILITY-MATRIX.md) |
| `GMA-UNIMPLEMENTED-MODEL-REPORT` | Unimplemented Model Report | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-UNIMPLEMENTED-MODEL-REPORT.md) |
| `GMA-UNRESOLVED-BOUNDARY-ITEMS` | Unresolved Boundary Items | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-UNRESOLVED-BOUNDARY-ITEMS.md) |
| `GMA-VALIDATION-ORDER` | Validation Order | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-VALIDATION-ORDER.md) |
| `GMA-WORKFLOW-REGISTRY` | Workflow Registry | PLANNED_NOT_YET_PRODUCED | [Consulter](lots/GMA-WORKFLOW-REGISTRY.md) |

## proposed_missing_specification (8)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `DRAFT-DELIVERY-REG` | Registre transversal des livrables | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-DELIVERY-REG.md) |
| `DRAFT-GLOBAL-CONTRACT` | Contrat directeur global unique | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-GLOBAL-CONTRACT.md) |
| `DRAFT-LOAD-CONTRACT` | Contrat de prise en charge d’un lot par un agent admis | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-LOAD-CONTRACT.md) |
| `DRAFT-REQ-TRACE` | Matrice exhaustive des exigences et des livrables | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-REQ-TRACE.md) |
| `DRAFT-SPRINT-GATES` | Contrats de passage inter-sprints | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-SPRINT-GATES.md) |
| `DRAFT-SPRINT-REG` | Registre de sprints et affectations | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-SPRINT-REG.md) |
| `DRAFT-STATUS-EVENTS` | Journal append-only des changements de statut | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-STATUS-EVENTS.md) |
| `DRAFT-TRACE-E2E` | Tests de traçabilité descendante et remontante | PROPOSED_NOT_REGISTERED | [Consulter](lots/DRAFT-TRACE-E2E.md) |

## structuring_case (4)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `ADOPT_EXISTING_REPOSITORY` | Cas 2 — adoption additive | PLANNED | [Consulter](lots/ADOPT_EXISTING_REPOSITORY.md) |
| `CREATE_NEW_REPOSITORY` | Cas 1 — création et bootstrap | DONE | [Consulter](lots/CREATE_NEW_REPOSITORY.md) |
| `LAB_EVOLUTION` | Cas 4 — laboratoire gouverné | PLANNED | [Consulter](lots/LAB_EVOLUTION.md) |
| `MAP_EXISTING_PROJECT` | Cas 3 — cartographie de projet | PLANNED | [Consulter](lots/MAP_EXISTING_PROJECT.md) |

## work_package (19)

| ID | Intitulé | Statut du modèle | Fiche |
|---|---|---|---|
| `GMC-G01` | Frontières modèle / stratégies / runtime / projections | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G01.md) |
| `GMC-G02` | Métamodèle, identités et contrats | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G02.md) |
| `GMC-G03` | Registre des domaines | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G03.md) |
| `GMC-G04` | Registre des capacités | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G04.md) |
| `GMC-G05` | Registre des composants | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G05.md) |
| `GMC-G06` | Objets, champs et relations | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G06.md) |
| `GMC-G07` | États et machines à états | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G07.md) |
| `GMC-G08` | Transitions, workflows, erreurs et reprises | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G08.md) |
| `GMC-G09` | Contrôles | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G09.md) |
| `GMC-G10` | Gates et autorités | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G10.md) |
| `GMC-G11` | Modèle des preuves | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G11.md) |
| `GMC-G12` | Cartographie modèle vers implémentation | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G12.md) |
| `GMC-G13` | Graphe global des dépendances | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G13.md) |
| `GMC-G14` | Comparateur sémantique | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G14.md) |
| `GMC-G15` | Comparaison fine des champs et contraintes | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G15.md) |
| `GMC-G16` | Conception de matérialisation des registres | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G16.md) |
| `GMC-G17` | Consommation du modèle par le Control Plane | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G17.md) |
| `GMC-G18` | Consommation commune des quatre cas | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G18.md) |
| `GMC-G19` | Assemblage, complétude et release du Governance Model | PLANNED_IN_BLUEPRINT | [Consulter](lots/GMC-G19.md) |

