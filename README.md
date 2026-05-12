# Migration de données médicales vers MongoDB avec Docker

Ce projet automatise la migration d'un dataset médical au format CSV vers une base de données MongoDB.
Il inclut des tests d'intégrité des données, un système d'authentification et un déploiement
entièrement containerisé avec Docker.

---

## Technologies utilisées

- **Python 3.14** — script de migration et tests
- **MongoDB** — base de données NoSQL
- **Docker & Docker Compose** — containerisation et orchestration
- **pytest** — tests unitaires et d'intégration
- **pymongo** — client Python pour MongoDB
- **pandas** — transformation des données
- **uv** — gestionnaire de dépendances Python

---

## Prérequis

- Docker et Docker Compose installés
- Git

> **Note** : Python, MongoDB et toutes les dépendances sont gérés automatiquement dans les containers Docker.
> `uv` est utilisé comme gestionnaire de dépendances Python et est installé directement dans l'image Docker.

---

## Structure du projet

```
p5_migration_mongoDB_Docker/
├── data/                          # Dossier contenant le CSV source
│   └── healthcare_dataset.csv
├── output/                        # Dossier contenant l'export CSV
│   └── export_healthcare.csv
├── test/
│   └── test_migration.py          # Tests unitaires et d'intégration
├── migrate.py                     # Script principal de migration
├── init_db.py                     # Script de création des utilisateurs MongoDB
├── Dockerfile                     # Image Docker de l'application Python
├── docker-compose.yml             # Orchestration des containers
├── .env                           # Variables d'environnement (non versionné)
├── .env.sample                    # Template des variables d'environnement
├── conftest.py                    # Configuration pytest
└── pyproject.toml                 # Dépendances Python (uv)
```

---

## Installation

1. Cloner le projet
```bash
git clone https://github.com/florentslmn/P5_migration_mongoDB_Docker.git
cd P5_migration_mongoDB_Docker
```

2. Configurer les variables d'environnement
```bash
cp .env.sample .env
```
Puis remplir les valeurs dans le fichier `.env`

3. Ajouter le dataset

Créer le dossier `data/`

```bash
mkdir data
```
Télécharger le [dataset Kaggle](https://www.kaggle.com/datasets/prasad22/healthcare-dataset) et le placer dans `data/`

4. Lancer le projet
```bash
docker-compose up --build
```

---

## Fonctionnement

Le projet repose sur deux containers Docker :

- **mongodb** — base de données MongoDB avec authentification activée
- **python-app** — application Python qui exécute les scripts dans l'ordre suivant :

1. `init_db.py` — crée les utilisateurs MongoDB avec leurs rôles (`app_user` en lecture/écriture, `reader_user` en lecture seule)
2. `pytest` — lance les 7 tests d'intégrité sur les données et la migration
3. `migrate.py` — transforme les données du CSV et les insère dans MongoDB

> Si les tests échouent, la migration ne se lance pas.

Un fichier d'export `export_healthcare.csv` est généré dans le dossier `output/` à la fin de la migration.

---

## Schéma de la base de données

**Base de données** : `healthcare`
**Collection** : `patients_records`

| Champ | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Identifiant unique généré automatiquement par MongoDB |
| `name` | String | Nom du patient |
| `age` | Integer | Âge du patient |
| `gender` | String | Genre du patient |
| `blood_type` | String | Groupe sanguin |
| `medical_condition` | String | Condition médicale diagnostiquée |
| `date_of_admission` | Date | Date d'admission |
| `doctor` | String | Nom du médecin |
| `hospital` | String | Nom de l'hôpital |
| `insurance_provider` | String | Assurance du patient |
| `billing_amount` | Float | Montant facturé |
| `room_number` | Integer | Numéro de chambre |
| `admission_type` | String | Type d'admission |
| `discharge_date` | Date | Date de sortie |
| `medication` | String | Médicament prescrit |
| `test_results` | String | Résultats des tests |

---

## Authentification

MongoDB est déployé avec l'authentification activée. Trois utilisateurs sont créés :

| Utilisateur | Rôle | Base de données | Description |
|-------------|------|-----------------|-------------|
| `admin` | root | `admin` | Super utilisateur créé au démarrage de MongoDB |
| `app_user` | readWrite | `healthcare`, `test_healthcare` | Utilisé par le script de migration |
| `reader_user` | read | `healthcare`, `test_healthcare` | Accès en lecture seule |

Les credentials sont définis dans le fichier `.env` (voir `.env.sample`).

---

## Tests

Les tests sont lancés automatiquement avant la migration via `pytest`.

### Tests sur la transformation des données (`transform_data`)

| Test | Description |
|------|-------------|
| `test_columns_name` | Vérifie que les colonnes sont bien renommées en minuscules avec underscores |
| `test_columns_type` | Vérifie les types des colonnes (int, float, datetime) |
| `test_row_count` | Vérifie qu'aucune ligne n'est perdue après transformation |
| `test_null_values` | Vérifie l'absence de valeurs nulles |
| `test_duplicated_values` | Vérifie l'absence de doublons |

### Tests sur l'insertion MongoDB (`insert_data`)

| Test | Description |
|------|-------------|
| `test_insert_data` | Vérifie que le bon nombre de documents est inséré |
| `test_mongodb_field_types` | Vérifie les types des champs stockés dans MongoDB |

Pour lancer les tests manuellement :
```bash
pytest test/test_migration.py -v
```
