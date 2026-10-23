# Import exact Construction GRT V2 — état actuel et historique

**Date de contrôle :** 2026-10-20  
**PR :** [#339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339) — DRAFT, sans merge.  
**Statut du corpus :** `412/412_SOURCE_FILES_PUBLISHED_AND_EXACT_BLOB_HASHES_VERIFIED` sur la branche de la PR.  
**Origine :** `GRT_Dossier_Directeur_Construction_V2_2026-10-16.zip` — SHA-256 original `475c4f40d1648baec414871a929bbfc8062b2150574fb23e32b1fa6f3ab2935d`.

## Contrôles d'intégrité

- Les 412 fichiers décompressés du ZIP original sont publiés **individuellement** sous [`construction-v2-source/`](./) avec leurs chemins relatifs conservés.
- **378** contrats individuels sous `lots/` ; **34** autres fichiers d'origine (registres, guides, manifestes et modèles).
- **412/412** chemins originaux uniques et présents ; **412/412** SHA-1 Git `blob` comparés sur les contenus exacts à l'arbre GitHub ; **0 différence**.
- **3 108 774 octets** originaux comparés ; le fichier de contrôle [`HUB_CONSTRUCTION_FILE_HASHES_V01.json`](../HUB_CONSTRUCTION_FILE_HASHES_V01.json) fournit chemin, taille, SHA-256 source et SHA-1 Git par fichier.
- Un fichier additionnel `README_IMPORT_STATUS.md` est le journal de publication, **hors des 412 fichiers du ZIP**.
- Les six morceaux antérieurs `construction-v2-exact-archive/part-00.b64` à `part-05.b64` forment un flux XZ incomplet : **ils ne servent pas de preuve**. Le corpus GitHub actuel repose sur les 412 fichiers extraits, et non sur ces morceaux.
- Le ZIP d'origine lui-même reste hors GitHub en tant que **fichier ZIP unique** ; tous ses 412 contenus textuels sont néanmoins présents sur la branche.

## Séparation des autorités et suites

Publication documentaire uniquement : elle ne valide ni le contrat directeur ST01 (#288), ni une identité HUB runtime, ni la disponibilité de 378 tâches `READY`, ni une session, un claim, une autorisation de mutation ou un déploiement. Le Control Plane et les autorités GSCC/GSE/GACR/F1 restent inchangés.

La branche et les contrôles CI sont à vérifier sur le HEAD final après publication ; pas de fusion automatique.

## Checkpoint historique conservé

Le checkpoint précédent mentionnait **25/412 fichiers publiés, 387 restants** ; il a été supersédé par l'import 412/412 ci-dessus. L'ancien état et sa date de référence restent traçables dans les commits antérieurs de la PR #339.
