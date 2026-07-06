# Guide d'utilisation — Ba7ath Data Catalog

Ce guide explique comment utiliser Ba7ath Data Catalog au quotidien, depuis l'enregistrement d'un fichier jusqu'à son audit et son exploitation dans un workflow de datajournalisme.

## Objectif du guide

L'application a été conçue pour répondre à une situation fréquente : une accumulation de fichiers hétérogènes dont on ne sait plus très bien l'origine, la qualité, l'historique ou le niveau de confiance. Le guide montre comment transformer ces fichiers en objets documentés, versionnés et auditables.

## Avant de commencer

Avant d'utiliser l'application, il est recommandé de préparer les éléments suivants :

- le fichier à enregistrer,
- les informations de source disponibles,
- la date d'extraction ou de collecte,
- la nature des traitements déjà appliqués,
- l'évaluation du risque juridique et PII,
- le contexte éditorial du dataset.

Même si certaines informations sont inconnues au départ, il est préférable de documenter ce qui est sûr plutôt que de laisser des champs ambigus ou trompeurs.

## Vue générale de l'application

Selon ton implémentation, l'application peut être organisée autour de plusieurs écrans ou sections :

- **Ingestion**,
- **Catalogue**,
- **Détail dataset**,
- **Historique des versions**,
- **Audit qualité**,
- **Audit d'intégrité**.

Chaque section répond à une question opérationnelle :

| Section | Question principale |
|---|---|
| Ingestion | Comment enregistrer proprement un nouveau fichier ? |
| Catalogue | Quels datasets existent déjà ? |
| Détail dataset | Que sait-on exactement d'un dataset donné ? |
| Versions | Quelles transformations a-t-il subies ? |
| Audit qualité | Peut-on l'exploiter sans risque méthodologique majeur ? |
| Audit d'intégrité | Le fichier a-t-il été modifié depuis son enregistrement ? |

## Démarrer l'application

### Lancement

Dans le dossier du projet :

```bash
streamlit run app.py
```

### Accès

Après lancement, Streamlit ouvre généralement l'application dans le navigateur à une adresse locale de type :

```text
http://localhost:8501
```

## Utiliser l'écran d'ingestion

L'écran d'ingestion sert à créer une nouvelle entrée dans le catalogue, ou une nouvelle version d'un dataset existant.

### 1. Importer un fichier

Téléverser un fichier supporté, par exemple :

- CSV,
- TSV,
- XLSX,
- XLS,
- JSON.

L'application peut lire le fichier, calculer son hash et produire un premier profil de structure.

### 2. Vérifier l'autodétection

Si le nom de fichier suit une convention comme :

```text
20260114_isie_resultats-legislatives_RAW.csv
```

l'application peut pré-remplir :

- la date d'extraction,
- la source,
- le sujet,
- l'état de traitement.

Cette autodétection fait gagner du temps, mais il faut toujours relire les champs avant validation.

### 3. Compléter les métadonnées

Renseigner autant que possible :

- titre du dataset,
- sujet,
- source,
- URL source,
- type de source,
- vecteur d'acquisition,
- date d'extraction,
- description,
- collecteur,
- auteur ou responsable,
- traitements appliqués,
- détails IA,
- validation légale,
- présence éventuelle de PII.

### 4. Choisir l'état de traitement

L'état de traitement décrit le niveau de transformation du fichier. Une convention simple peut être :

| État | Signification |
|---|---|
| RAW | Fichier brut, non modifié ou quasi brut. |
| PROCESSING | Fichier en cours de nettoyage, de fusion ou d'enrichissement. |
| CLEAN | Version propre et structurée pour l'analyse. |

Tu peux ensuite étendre cette taxonomie si besoin, par exemple avec `ENRICHED`, `MATCHED` ou `PUBLISHED`.

### 5. Enregistrer une version dérivée

Si le fichier est une transformation d'un dataset déjà présent :

1. sélectionner la version parente,
2. décrire les traitements appliqués,
3. enregistrer le nouveau fichier comme nouvelle version,
4. vérifier que le lineage est correctement conservé.

Exemple :

- version 1 : export brut,
- version 2 : nettoyage des doublons,
- version 3 : normalisation des identifiants,
- version 4 : jointure avec un référentiel externe.

## Lire le profil d'un dataset

Après ingestion, l'application peut produire une fiche synthétique avec :

- nombre de lignes,
- nombre de colonnes,
- liste des colonnes,
- types détectés,
- nulls,
- doublons,
- aperçu des premières lignes,
- taille mémoire,
- hash de schéma.

Cette vue sert à répondre rapidement à trois questions :

- le fichier est-il lisible ?
- le schéma semble-t-il cohérent ?
- y a-t-il des problèmes évidents avant l'analyse ?

## Utiliser le catalogue

Le catalogue sert à parcourir tous les datasets enregistrés.

### Rechercher

Chercher par :

- nom,
- sujet,
- source,
- état,
- mot-clé,
- type de risque,
- score qualité.

### Filtrer

Les filtres les plus utiles sont généralement :

- source,
- période,
- présence de PII,
- validation légale,
- statut de qualité,
- type de fichier,
- dataset avec ou sans dérivations.

### Identifier rapidement les jeux critiques

Dans un usage newsroom, certains signaux doivent être visibles immédiatement :

- faible score qualité,
- colonnes sensibles,
- absence de parent sur une version dérivée,
- fichier modifié après enregistrement,
- fort taux de nulls,
- nombreuses duplications.

## Comprendre le détail dataset

L'écran détail dataset doit être la fiche de référence du jeu de données. Il rassemble idéalement :

- identité du dataset,
- description,
- source,
- versions disponibles,
- dernier profil,
- historique d'audits,
- signaux de risque,
- traitements documentés,
- fichiers liés,
- notes d'usage.

C'est la page la plus utile pour transmettre un dataset à un collègue sans avoir à lui expliquer tout le contexte oralement.

## Lire le lineage

Le lineage montre la généalogie des versions.

Exemple de lecture :

```text
v1 RAW -> v2 CLEAN -> v3 MATCHED -> v4 PUBLISHED
```

Le lineage permet de comprendre :

- quelle version est l'origine,
- quelles étapes ont été appliquées,
- quelle version peut être reproduite,
- quelle version a servi à l'analyse finale.

Bon réflexe : ne jamais écraser un fichier important. Enregistrer une nouvelle version est presque toujours préférable à modifier silencieusement une version existante.

## Utiliser l'audit qualité

L'audit qualité ne remplace pas l'analyse humaine, mais il donne un diagnostic rapide.

### Signaux typiques

L'application peut calculer ou signaler :

- complétude,
- unicité,
- cohérence simple,
- colonnes sensibles,
- flags qualité,
- changements de schéma.

### Interpréter un score

Un score élevé signifie qu'aucune anomalie structurelle majeure n'a été détectée, pas que le dataset est vrai ou méthodologiquement neutre. À l'inverse, un score faible indique qu'un contrôle humain s'impose avant toute analyse publique.

### Réflexes recommandés

- vérifier les colonnes clés,
- repérer les taux de nulls anormaux,
- identifier les doublons,
- relire les colonnes sensibles,
- comparer avec une version précédente si le schéma a changé.

## Utiliser l'audit d'intégrité

L'audit d'intégrité sert à comparer un fichier avec son empreinte enregistrée.

### Quand l'utiliser

Utiliser cet audit lorsque tu veux savoir si un fichier :

- est strictement identique à l'original enregistré,
- a été modifié,
- a été corrompu,
- correspond bien à une pièce de preuve ou à une version de référence.

### Procédure

1. choisir la version de référence dans l'application,
2. téléverser le fichier à tester,
3. lancer le calcul du hash,
4. comparer le SHA-256 obtenu avec l'empreinte enregistrée.

### Interprétation

| Résultat | Signification |
|---|---|
| Hash identique | Le fichier correspond à la version de référence enregistrée. |
| Hash différent | Le fichier a changé, a été altéré ou n'est pas la même version. |

Un hash différent ne signifie pas nécessairement fraude, mais signifie toujours qu'il faut investiguer la différence.

## Bonnes pratiques d'usage

### Documenter tôt

Il vaut mieux enregistrer un dataset dès son arrivée, même avec une fiche incomplète, plutôt que d'attendre et perdre le contexte de collecte.

### Versionner systématiquement

Dès qu'un traitement significatif est appliqué, créer une nouvelle version.

### Décrire les transformations

Ne pas écrire seulement "nettoyage". Préciser par exemple :

- suppression des doublons sur `supplier_id`,
- normalisation UTF-8,
- conversion date JJ/MM/AAAA vers ISO,
- jointure avec table des entreprises,
- détection de catégories via LLM,
- revue humaine manuelle après scoring.

### Séparer qualité et vérité

Un dataset peut être techniquement propre et pourtant incomplet, biaisé ou trompeur. Le score qualité renseigne surtout sur la structure et la lisibilité, pas sur la vérité du contenu.

### Garder le contexte éditorial

Un bon catalogue de données ne contient pas seulement des colonnes et des hashes. Il doit aussi dire à quoi sert le dataset, dans quelle enquête il s'inscrit, et avec quelles limites il peut être utilisé.

## Workflow recommandé en rédaction

### Workflow court

1. réception ou collecte,
2. ingestion,
3. profilage,
4. qualification source et risque,
5. versioning après transformation,
6. audit avant exploitation,
7. documentation finale.

### Workflow collaboratif

| Rôle | Action recommandée |
|---|---|
| Reporter / chercheur | Enregistre la source et le contexte de collecte. |
| Datajournaliste | Profile, nettoie, transforme et documente les versions. |
| Éditeur / responsable | Vérifie le niveau de confiance, les risques et l'usage prévu. |
| Juriste / responsable conformité | Relit les datasets sensibles ou contenant des données personnelles. |

## Exemples d'usage concrets

### Marchés publics

Un export brut est ingéré comme `RAW`, puis nettoyé, normalisé et joint à un référentiel d'entreprises. Chaque étape devient une nouvelle version documentée.

### Résultats électoraux

Des versions successives d'un portail officiel peuvent être comparées pour détecter des changements de schéma, des corrections tardives ou des retraits de lignes.

### OSINT documentaire

Un fichier obtenu par veille ou téléchargement manuel peut être hashé immédiatement, puis enrichi dans une version dérivée tout en conservant la chaîne de preuve.

## Erreurs fréquentes à éviter

- importer un fichier sans source,
- écraser un dataset sans créer de nouvelle version,
- oublier de documenter un traitement important,
- confondre score qualité et validité factuelle,
- ne pas signaler la présence de PII,
- utiliser une version dérivée sans indiquer son parent,
- publier à partir d'un fichier non audité.

## Dépannage rapide

### Le fichier ne se charge pas

Vérifier :

- l'extension,
- l'encodage,
- la taille,
- la validité du fichier,
- la présence de dépendances comme `openpyxl` pour Excel.

### Le schéma paraît incohérent

Causes possibles :

- séparateur CSV incorrect,
- première ligne mal interprétée,
- colonnes fusionnées,
- encodage abîmé,
- types mixtes dans une même colonne.

### Le hash change alors que le contenu semble identique

Le fichier a peut-être été réexporté, réencodé ou modifié dans un détail invisible à l'œil nu. Une égalité visuelle ne garantit pas une égalité binaire.

### L'audit qualité donne un mauvais score

Ce score doit déclencher une revue, pas forcément un rejet immédiat. Il faut regarder les raisons exactes : nulls, doublons, colonnes sensibles, schéma, volume, etc.

## Conseils pour un usage avancé

- associer l'application à un dépôt Git pour les scripts de transformation,
- conserver les notebooks ou scripts de traitement liés aux versions,
- produire un passeport dataset avant publication,
- relier chaque dataset à une enquête, un sujet ou une hypothèse,
- garder des captures d'écran ou documents de source pour les cas sensibles,
- utiliser le lineage comme support de relecture éditoriale.

## Conclusion opérationnelle

Ba7ath Data Catalog est particulièrement utile lorsqu'il devient une habitude d'équipe. Son intérêt ne vient pas seulement du hash ou du stockage, mais de la discipline documentaire qu'il impose : nommer, décrire, versionner, auditer et contextualiser chaque dataset important.
