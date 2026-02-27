# refactory_project
Python refactoring project
Includes **formatter (Black)**, **linter (Pylint/Flake8)**, **type checking (Mypy)**, and **unit tests (Pytest)**.

## 1. Installation

## Prérequis
- Python version 3.10+
- Poetry version 1.6+
- Git (pour cloner le projet)

## Commandes
```bash
# Cloner le projet
git clone https://github.com/WorkFlowCoder/refactory_project.git
cd refactory_project

# Installer Poetry si nécessaire
curl -sSL https://install.python-poetry.org | python3 -
```
## Exécution
```bash
#Exécuter le code non factorisé
python legacy/order_report_legacy.py
# Exécuter le code refactorisé
poetry run python src/main.py
### Exécuter les tests
poetry run pytest
```

## Comparatif entre les sorties
Le comparatif ce fait de la façon suivante :
```bash
poetry run pytest tests/test_report_writer.py
```

## Refactoring

1. **Suppression des variables inutiles** : Nettoyage rapide du code pour améliorer la lisibilité et faciliter la compréhension.
Les variables superflues ont été retirées pour que chaque ligne ait un rôle clair.

2. **Séparation du code en fonctions** : Chaque fonction répond maintenant à un objectif précis (calcul des remises, taxes, frais de port, formatage du rapport).
Cela permet d’avoir un code plus aéré, facile à lire et à maintenir.

3. **Création de classes pour les entités** : Les entités comme *Customer* ou *Product* peuvent désormais être représentées par des objets avec des attributs.
Cela apporte une meilleure compréhension du code et une base solide pour l’évolution du projet, en facilitant la maintenance et l’ajout de nouvelles fonctionnalités.

4. **Création de services** : Les fonctions ont été regroupées selon leur rôle (calculs, gestion des remises, gestion des taxes, etc.).
Cette structuration par service à responsabilité unique permet d’avoir un code modulable et plus clair, tout en préparant l’architecture pour de futures extensions.

## Ce qui n'a pas été fait (par manque de temps)

Avec plus de temps, plusieurs éléments serait à continuer :

- Les tests unitaires n’ont pas encore été écrits, ce qui est essentiel pour sécuriser les futurs changements.

- Une séparation plus fine des services pourrait être envisagée pour aerer encore plus calculations.py.

## Compromis Assumés

- Nombre de services : Avec plus de temps, il aurait été possible de créer davantage de services, chacun avec une responsabilité très précise, ce qui aurait encore amélioré la lisibilité et la modularité du code.

## Pistes d'Amélioration Future

- Réalisation d'une documentation

- Il manque des commentaires explicatifs sur certaines fonctions complexes

- Ajouter des logs pour le suivi des calculs