# Import exact Construction GRT V2 — état de publication

**Date :** 2026-10-20
**PR :** [#339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339), DRAFT ; aucun merge.
**Objet :** dossier documentaire candidat, ni identité HUB adoptée, ni authority runtime.
**Source originale :** `GRT_Dossier_Directeur_Construction_V2_2026-10-16.zip`.
**SHA-256 du ZIP local vérifié :** `475c4f40d1648baec414871a929bbfc8062b2150574fb23e32b1fa6f3ab2935d`.

## Contrôle d'import

- **Total source : 412 fichiers texte**, dont **378 fiches de pièces** dans `lots/`.
- **Lot 01/17 : 25 fichiers publiés** sous ce répertoire avec les noms et contenus originaux.
- **Vérification : 25/25 comparaisons exactes** entre le JSON de transit local et les fichiers GitHub relus sur le SHA `8e16dc02280fb25da6a07c20ddc609055e3c09c5`.
- **Restants : 387 fichiers** (lots 02/17 à 17/17), NON PUBLIÉS à cette étape.
- Les six fragments `construction-v2-exact-archive/part-00.b64` à `part-05.b64` constituent un flux XZ tronqué ; ils ne prouvent pas la présence de l'archive complète et ne sont pas utilisés comme preuve d'import. Les conserver pour audit historique.
- Le [crosswalk existant](../HUB_CONSTRUCTION_CROSSWALK_V01.csv) est un **index documentaire de 378 pièces**, non la preuve que 378 contenus sont tous disponibles.

## Prochaine action sûre

Importer les 387 fichiers originaux restants en préservant le chemin `docs/audits/2026-10-19/construction-v2-source/<relative-source-path>`, vérifier pour chaque lot les contenus exacts et les noms, puis reconstituer un manifeste final d'inventaire `412/412`. Ne pas déclarer la publication intégrale avant contrôle exhaustif.

Rapprocher les identifiants HUB divergents documentés dans la PR, **sans choisir silencieusement un ID**. Garder la séparation de la proposition ST01 #288 et du Control Plane exécutable. Tous les contenus restent `DOCUMENTARY_DRAFT` ; aucun nouveau bus, tâche READY, session, claim, autorisation ou modification de `main`.

## Règles anti-collision

- Ne pas effacer ou remplacer les six fragments historiques ni les nouveaux documents HUB.
- Vérifier le HEAD de la PR et effectuer des mises à jour optimistes.
- Ne pas modifier les gates P0, les JSON GACR ou le Control Plane source depuis le paquet candidat.
- Ne pas créer d'autre PR ou issue pour cet import et ne jamais fusionner automatiquement.
