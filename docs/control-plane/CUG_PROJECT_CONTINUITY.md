# CUG — création gouvernée et continuité de projet

Ce raccordement étend le parcours CASE 1 sans rouvrir sa clôture historique.
Le workflow central GRT reste seul responsable de la préparation et du handoff.
L'entrée locale reste distribuée aux dépôts clients. Cette extension ne crée
ni registre MCP, ni répertoire S1/S2, ni pipeline de déploiement.

## Demande machine

Le contrat additif de l'événement existant `governed_request_start` accepte
`objective` et `creation: {owner, name, visibility}`. Les valeurs de propriétaire
sont les labels CASE 1 existants. L'événement doit être émis par le bot de
l'installation CUG autorisée dans GRT. Le flux historique sans `creation`
conserve son comportement et sa configuration.

Le plan de contrôle requiert une configuration indépendante de l'ancienne App.
Configurer `GOVERNED_CUG_APP_CLIENT_ID` et `GOVERNED_CUG_BOT_LOGIN` comme
variables Actions et `GOVERNED_CUG_APP_PRIVATE_KEY` comme secret. Avant
d'admettre une demande machine, le workflow rapproche ces valeurs avec l'App
authentifiée auprès de GitHub, d'ID numérique 5417646. Le jeton MCP central
existant est distinct. La voie CUG ne doit pas servir à accorder des droits
d'installation, de registre ou de production.

## Chronologie et preuves

| Phase | Entrée | Sortie |
|---|---|---|
| Demande | Acteur CUG vérifié, objectif, propriétaire, nom et visibilité | État de demande GRT, ID projet et plan CASE 1 |
| PREP-001 | Plan et jeton de l'installation CUG du compte | Dépôt GitHub créé, ID numérique observé, HEAD initial et projection de continuité |
| PREP-002 à 004 | Bootstrap, observation d'infrastructure, référence GitHub | Preuves préparatoires et handoff central exact-HEAD |
| Entrée locale | Handoff, repo exact et éventuelle projection | État local, même continuité, questions applicables |
| Découverte optionnelle | Choix et approbation de découverte, moyen d'accès selon le mode | Provisionnement séparé de la preuve de l'appel MCP |
| Baseline | Réponses, résultats, approbation | État local, reçu versionné, handoff et point de reprise |

Le workflow observe automatiquement PREP-002 à PREP-004 et déclenche
l'entrée locale si la preuve exacte du bootstrap est disponible. Si le
bootstrap n'est pas encore attesté après la fenêtre d'observation, la demande
reste à PREP-002 et la commande gouvernée de reprise réobserve cette étape.
Le questionnaire local, ses validations et le reçu gardent leurs transitions
historiques. Cette version ne fournit pas encore de boucle autonome pour les
consommer ni de point d'entrée déployé dans le serveur MCP. Une cible qui existe
déjà au moment de PREP-001 sur la voie CUG est arrêtée pour réconciliation,
pas adoptée sur la seule concordance de son nom. Le parcours normal n'est
pas utilisé pour rejouer une création incertaine.

## Même identifiant sur les deux côtés

Pour un nouveau projet CASE 1 initié par CUG, `project_continuity_id`
est attribué à l'ouverture de la demande centrale, avant la création du
dépôt. Il associe l'ID du plan de contrôle GRT à l'ID de sa demande. Le dépôt
GitHub est ensuite rattaché par son propre ID numérique. L'identité projet
ne dépend ni du dépôt cible, ni du serveur, ni de la session ou du run. Les dépôts historiques n'ont pas d'identifiant attribué par défaut.
Les anciens reçus et leurs autorisations restent inchangés.

Le workflow central transmet la projection dans son handoff. Le dépôt la
vérifie avec l'identité du dépôt connue de GitHub Actions, puis la matérialise
dans `.governance/local-entry/state.json` et le reçu local. Le futur parcours
de liaison pourra référencer le même ID depuis S1/S2. Dans cette phase,
`server_binding_status` reste `NOT_BOUND`. L'ID n'est ni une session, ni un
jeton, ni une autorisation, ni une preuve de rattachement au registre MCP.
