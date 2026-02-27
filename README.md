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
### Exécuter les testes
poetry run pytest
```

## Comparatif entre les sorties
Le comparatif ce fait de la façon suivante :
```bash
poetry run pytest tests/test_report_writer.p
```

## Exécution
```bash
#Exécuter le code non factorisé
python legacy/order_report_legacy.py
# Exécuter le code refactorisé
poetry run python src/main.py
### Exécuter les testes
poetry run pytest
```

## Choix de Refactoring

// A venir

## Solutions Apportées

// A venir

### Architecture Choisie

// A venir

### Exemples Concrets

// A venir

**Exemple 1 : [Nom du refactoring]**
- Problème : [code smell spécifique]
- Solution : [approche retenue]

**Exemple 2 : [Autre refactoring]**
- ...

## Limites et Améliorations Futures

// A venir