# Ba7ath Data Catalog

Ba7ath Data Catalog est une application Streamlit pensée pour les datajournalistes, enquêteurs et analystes OSINT qui doivent gérer un grand volume de jeux de données, en conserver la traçabilité et documenter leur qualité, leur provenance et leur historique de transformation.

L'objectif de l'application est de transformer un simple répertoire de fichiers en un catalogue de travail documenté, exploitable et auditable. Elle ne sert pas uniquement à stocker des datasets : elle aide à savoir d'où vient chaque fichier, comment il a été produit, s'il a changé, s'il contient des risques, et s'il est suffisamment fiable pour une analyse ou une publication.

## Problème traité

Dans de nombreux workflows de datajournalisme, les jeux de données s'accumulent rapidement : exports CSV, réponses API, fichiers Excel, dumps JSON, copies nettoyées, versions enrichies, jeux fusionnés, dérivés produits avec scripts ou LLM, etc. Très vite, plusieurs questions deviennent difficiles à résoudre :

- Quel est le fichier d'origine ?
- Quelle version est la plus récente ?
- Quelles transformations ont été appliquées ?
- Peut-on vérifier qu'un fichier n'a pas été altéré ?
- Quelle est la qualité structurelle du dataset ?
- Y a-t-il des données personnelles ou des risques légaux ?
- Peut-on justifier le dataset devant une rédaction, un partenaire, un avocat ou un lecteur ?

Ba7ath Data Catalog apporte une réponse à ces problèmes en combinant quatre logiques dans une seule application :

- un **catalogue de datasets**,
- un **registre de versions**,
- un **journal de transformations**,
- un **système d'audit d'intégrité et de qualité**.

## Fonctionnalités principales

### 1. Ingestion structurée

L'application permet d'enregistrer un dataset avec des métadonnées documentées :

- titre,
- sujet,
- source,
- type de source,
- vecteur d'acquisition,
- date d'extraction,
- auteur ou collecteur,
- description,
- validation légale,
- présence de données personnelles,
- détails IA,
- traitements appliqués.

Elle peut aussi détecter automatiquement une partie des métadonnées si le nom de fichier suit une convention comme :

```text
20250701_ministere-finances_marches-publics_RAW.csv
```

### 2. Versioning et lineage

Chaque dataset logique peut contenir plusieurs versions physiques. Cela permet de distinguer :

- le dataset comme objet éditorial,
- la version comme fichier concret,
- les relations de dérivation entre versions.

L'application peut ainsi documenter un flux du type :

```text
RAW -> CLEAN -> ENRICHED -> MATCHED -> PUBLISHED
```

ou encore :

```text
source officielle -> extraction CSV -> nettoyage -> jointure -> scoring -> export final
```

### 3. Profilage automatique

À l'ingestion, l'application peut produire un premier profil de données :

- nombre de lignes,
- nombre de colonnes,
- noms de colonnes,
- types probables,
- taux de valeurs manquantes,
- doublons,
- aperçu des données,
- snapshot de schéma.

Cette étape permet d'obtenir une vue rapide sur l'état réel du dataset sans devoir l'ouvrir manuellement dans Excel ou un notebook.

### 4. Audit d'intégrité

Chaque version est associée à une empreinte SHA-256. Cela permet de :

- vérifier qu'un fichier local correspond exactement à une version enregistrée,
- détecter une modification ou une corruption,
- documenter une chaîne de preuve,
- justifier qu'un artefact n'a pas été altéré depuis son enregistrement.

### 5. Audit qualité

L'application peut calculer des signaux simples mais utiles pour le travail journalistique :

- score de complétude,
- score d'unicité,
- score de cohérence simple,
- détection de colonnes potentiellement sensibles,
- drapeaux qualité,
- diff de schéma entre versions.

### 6. Gouvernance éditoriale

Le projet est pensé pour aller au-delà du stockage technique. Il vise aussi à aider une rédaction ou une cellule d'enquête à décider :

- si un dataset est exploitable,
- s'il est sensible,
- s'il demande une revue humaine,
- s'il peut être partagé,
- et s'il est prêt pour publication.

## Architecture recommandée

Le projet est structuré autour d'une séparation claire entre données, logique métier et interface :

```text
ba7ath_data_catalog/
├── app.py
├── database/
│   ├── connection.py
│   ├── schema.sql
│   └── repositories/
│       ├── datasets.py
│       ├── versions.py
│       ├── profiles.py
│       └── audits.py
├── services/
│   ├── ingest_service.py
│   ├── quality_audit_service.py
│   ├── integrity_service.py
│   └── lineage_service.py
├── ui/
│   ├── dashboard_ingest.py
│   ├── dashboard_catalog.py
│   ├── dashboard_dataset_detail.py
│   └── components.py
├── utils/
│   ├── hashing.py
│   ├── parsing.py
│   └── formatting.py
└── requirements.txt
```

## Modèle conceptuel

Le modèle distingue plusieurs objets métier :

| Objet | Rôle |
|---|---|
| Dataset | Entité logique représentant un corpus ou un jeu de données suivi dans le temps. |
| Version | Fichier physique concret lié à un dataset. |
| Profil | Résumé structurel calculé à partir d'une version. |
| Audit | Résultat d'un contrôle d'intégrité, de qualité ou de schéma. |
| Transformation | Étape documentée appliquée à une version. |
| Source | Origine déclarée du dataset, avec son contexte de collecte. |

Cette distinction est importante, car un même dataset peut exister en plusieurs versions, et chaque version peut avoir une qualité, un schéma et un niveau de risque différents.

## Technologies

Le projet repose sur un socle volontairement simple et portable :

- **Python** pour la logique métier,
- **Streamlit** pour l'interface,
- **SQLite** pour la persistance locale,
- **Pandas** pour la lecture et le profilage de base,
- **hashlib** pour les empreintes cryptographiques,
- **JSON** pour certains champs structurés ou journaux de transformation.

Ce choix permet un déploiement léger, pratique pour des cellules d'enquête, des formations ou des équipes qui veulent un outil local sans infra lourde.

## Installation

### 1. Cloner le projet

```bash
git clone <repo_url>
cd ba7ath_data_catalog
```

### 2. Créer un environnement virtuel

Sous Linux ou macOS :

```bash
python -m venv .venv
source .venv/bin/activate
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Exemple minimal de `requirements.txt` :

```text
streamlit
pandas
openpyxl
```

### 4. Lancer l'application

```bash
streamlit run app.py
```

## Configuration

Configuration minimale typique :

- base SQLite locale,
- dossier de stockage pour les fichiers ingérés,
- convention de nommage recommandée,
- seuils simples pour les audits qualité.

Exemple de paramètres à centraliser :

```python
DB_PATH = "data/catalog.db"
STORAGE_DIR = "data/uploads"
DEFAULT_PROCESSING_STATES = ["RAW", "PROCESSING", "CLEAN"]
ALLOWED_EXTENSIONS = ["csv", "tsv", "xlsx", "xls", "json"]
```

## Convention de nommage recommandée

Une convention claire facilite énormément la recherche, le tri et l'autocomplétion. Le format conseillé est :

```text
YYYYMMDD_source_sujet_etat.ext
```

Exemples :

```text
20260114_isie_resultats-legislatives_RAW.csv
20260203_tuneps_marches-publics_PROCESSING.xlsx
20260205_openalex_universites-clean_CLEAN.json
```

Bonnes pratiques :

- utiliser des tirets pour les espaces,
- garder des noms courts mais explicites,
- conserver l'état de traitement dans le nom,
- éviter les caractères spéciaux,
- documenter chaque dérivation importante dans l'application.

## Workflow conseillé

### Étape 1. Ingestion

Importer le fichier et compléter les métadonnées de base.

### Étape 2. Profilage

Laisser l'application produire un profil automatique, puis relire les colonnes, les nulls et les doublons.

### Étape 3. Qualification

Documenter la source, le risque PII, la validation légale et les éventuels traitements IA.

### Étape 4. Versioning

Enregistrer toute transformation importante comme une nouvelle version liée à une version parente.

### Étape 5. Audit

Lancer les vérifications d'intégrité et les audits qualité avant diffusion interne ou publication.

### Étape 6. Exploitation

Utiliser le dataset pour analyse, visualisation, scraping complémentaire, matching ou publication, tout en conservant la chaîne de preuve.

## Cas d'usage

### Enquête journalistique

Suivre plusieurs extractions d'un portail public, comparer leur schéma et documenter les changements.

### Travail collaboratif en rédaction

Centraliser les versions d'un dataset partagé et éviter les fichiers nommés `final_v2_really_final.xlsx`.

### OSINT et veille

Garder la trace d'un fichier collecté en ligne, de son origine, de son hash et de son historique de transformation.

### Formation

Utiliser l'application comme support pédagogique pour enseigner la traçabilité, la documentation et l'évaluation d'un dataset.

## Exemples de signaux d'alerte utiles

L'application peut aider à remonter des situations comme :

- dataset vide,
- schéma instable,
- taux élevé de valeurs manquantes,
- présence de doublons,
- colonnes sensibles,
- absence de validation légale,
- transformation par IA sans revue humaine,
- version dérivée sans parent clairement documenté.

## Limites actuelles

Le projet reste volontairement léger et local. Dans sa forme de base, il ne remplace pas :

- un data catalog d'entreprise,
- un système de stockage distribué,
- un data warehouse,
- une GED complète,
- un système avancé de data quality enterprise.

Ses limites typiques sont :

- SQLite peu adapté aux usages multi-utilisateurs intensifs,
- profilage simple par rapport à Great Expectations ou Soda,
- détection PII fondée surtout sur les noms de colonnes,
- besoin de conventions d'équipe pour être pleinement efficace,
- nécessité de revue humaine sur les signaux critiques.

## Roadmap suggérée

Évolutions recommandées :

- diff avancé entre versions,
- export de passeport dataset en Markdown/PDF,
- rapport de chaîne de preuve,
- watchlist de sources,
- détection de drift de schéma,
- moteur de recherche plus avancé,
- taxonomie de tags par enquête,
- gestion des pièces jointes de preuve,
- scoring éditorial multi-critères,
- authentification et rôles.

## Contribution

Pour contribuer utilement au projet :

1. ajouter ou améliorer un module métier,
2. garder les repositories simples et testables,
3. éviter de mélanger logique Streamlit et logique métier,
4. documenter chaque nouvelle table ou règle de score,
5. ajouter des exemples de datasets de test,
6. écrire des tests unitaires sur les services critiques.

## Principes de conception

Ba7ath Data Catalog repose sur quelques principes forts :

- **traçabilité avant confort**,
- **version explicite avant écrasement silencieux**,
- **métadonnées éditoriales avant simple stockage**,
- **auditabilité avant automatisation aveugle**,
- **lecture humaine avant sophistication inutile**.

Ces principes sont particulièrement adaptés au datajournalisme, où un dataset n'est jamais un simple fichier technique mais souvent une pièce de travail, de preuve, de vérification ou de publication.

## Licence

Choisir une licence adaptée à l'usage visé, par exemple MIT pour un projet ouvert ou une licence interne si l'outil reste réservé à une rédaction ou une organisation.
