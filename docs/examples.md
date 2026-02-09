---
layout: default
title: Exemples
nav_order: 5
description: "Cas d'usage concrets et exemples pratiques"
permalink: /examples
---

# Exemples
{: .no_toc }

Découvrez des cas d'usage concrets et des exemples pratiques pour utiliser DocGen dans différents contextes.
{: .fs-6 .fw-300 }

## Table des matières
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 🐍 Projet Python simple

### Structure du projet

```
mon-projet/
├── src/
│   └── mon_app/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Commandes

```bash
# 1. Initialiser DocGen
cd mon-projet
docgen init

# 2. Vérifier la détection
docgen scan
```

**Sortie attendue :**

```
Project: mon-projet
Repo: /path/to/mon-projet

╭────── Stacks ──────╮
│ python   1.00      │
╰────────────────────╯

╭────── Commands ────╮
│ test   pytest      │
│ lint   ruff check  │
╰────────────────────╯

Detected files:
- pyproject.toml
- requirements.txt

Package manager: pip
Python tooling: pytest
```

```bash
# 3. Générer la documentation
docgen build --force
```

### Résultat

```
mon-projet/
├── DocGen/
│   ├── README.md           # Documentation générée
│   ├── ARCHITECTURE.md     # Architecture
│   └── index.md           # GitHub Pages
├── docgen.yaml            # Configuration
└── ...
```

---

## 📦 Projet Node.js/TypeScript

### Structure du projet

```
my-app/
├── src/
│   ├── index.ts
│   ├── routes/
│   └── services/
├── tests/
│   └── index.test.ts
├── package.json
├── tsconfig.json
└── README.md
```

### Configuration

```yaml
# docgen.yaml
output_dir: docs
exclude:
  - .git/
  - node_modules/
  - dist/
  - coverage/
  - "*.log"
readme_target: output
enable_github_pages: true
enable_doxygen_block: false
```

### Commandes

```bash
docgen init
docgen scan --format text
docgen build --force
```

**Détection attendue :**

- Stack : `node`, `typescript`
- Commandes : `npm start`, `npm test`, `npm run build`
- Fichiers : `package.json`, `tsconfig.json`

---

## 🐳 Projet avec Docker

### Structure du projet

```
dockerized-app/
├── docker-compose.yml
├── Dockerfile
├── app/
│   ├── main.py
│   └── requirements.txt
└── README.md
```

### Configuration

```yaml
# docgen.yaml
output_dir: DocGen
exclude:
  - .git/
  - __pycache__/
  - venv/
readme_target: output
enable_github_pages: false
enable_doxygen_block: false
```

### Commandes

```bash
docgen init
docgen scan
```

**Sortie attendue :**

```
Stacks:
- python (1.00)
- docker (0.90)

Commands:
- run: docker-compose up
- test: pytest
- build: docker-compose build

Detected files:
- Dockerfile (docker)
- docker-compose.yml (docker)
- requirements.txt (config)
```

```bash
docgen build --force
```

---

## 🏗️ Monorepo multi-services

### Structure du projet

```
monorepo/
├── services/
│   ├── api/
│   │   ├── package.json
│   │   └── src/
│   ├── web/
│   │   ├── package.json
│   │   └── src/
│   └── worker/
│       ├── pyproject.toml
│       └── src/
├── docker-compose.yml
└── README.md
```

### Stratégie de documentation

#### Option 1 : Documentation globale

```bash
# À la racine
docgen init
docgen build --force
```

#### Option 2 : Documentation par service

```bash
# API
cd services/api
docgen init --config docgen.api.yaml
docgen build

# Web
cd services/web
docgen init --config docgen.web.yaml
docgen build

# Worker
cd services/worker
docgen init --config docgen.worker.yaml
docgen build
```

### Configuration globale

```yaml
# docgen.yaml (racine)
output_dir: documentation
exclude:
  - .git/
  - "**/node_modules/"
  - "**/venv/"
  - "**/dist/"
  - "**/build/"
readme_target: output
enable_github_pages: true
enable_doxygen_block: false
```

---

## 🔬 Projet C++ avec Doxygen

### Structure du projet

```
cpp-lib/
├── include/
│   └── mylib/
│       ├── core.h
│       └── utils.h
├── src/
│   ├── core.cpp
│   └── utils.cpp
├── tests/
│   └── test_core.cpp
├── CMakeLists.txt
├── Doxyfile
└── README.md
```

### Configuration

```yaml
# docgen.yaml
output_dir: docs/api
exclude:
  - .git/
  - build/
  - cmake-build-*/
  - "*.o"
  - "*.a"
readme_target: output
enable_github_pages: true
enable_doxygen_block: true
```

### Génération avec Doxygen

```bash
# Initialiser
docgen init

# Scanner
docgen scan

# Générer avec Doxygen
docgen build --doxygen --force
```

**Résultat :**

```
cpp-lib/
├── docs/
│   ├── api/
│   │   ├── README.md
│   │   ├── ARCHITECTURE.md
│   │   └── index.md
│   └── html/              # Généré par Doxygen
│       ├── index.html
│       └── ...
└── ...
```

---

## 🚀 Intégration CI/CD

### GitHub Actions

Créez `.github/workflows/docs.yml` :

```yaml
name: Generate Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install DocGen
        run: |
          pip install -e .
      
      - name: Generate documentation
        run: |
          docgen build --force
      
      - name: Commit documentation
        run: |
          git config user.name "DocGen Bot"
          git config user.email "bot@docgen.io"
          git add DocGen/
          git commit -m "docs: Update auto-generated documentation [skip ci]" || exit 0
          git push
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./DocGen
```

### GitLab CI

Créez `.gitlab-ci.yml` :

```yaml
stages:
  - docs

generate_docs:
  stage: docs
  image: python:3.11
  
  script:
    - pip install -e .
    - docgen build --force
    - git config user.name "DocGen Bot"
    - git config user.email "bot@docgen.io"
    - git add DocGen/
    - git commit -m "docs: Update documentation" || exit 0
    - git push origin $CI_COMMIT_REF_NAME
  
  only:
    - main
    - develop

pages:
  stage: docs
  image: python:3.11
  
  script:
    - pip install -e .
    - docgen build --force
    - mv DocGen public
  
  artifacts:
    paths:
      - public
  
  only:
    - main
```

### Jenkins

Créez `Jenkinsfile` :

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -e .'
            }
        }
        
        stage('Generate Documentation') {
            steps {
                sh 'docgen build --force'
            }
        }
        
        stage('Publish') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    git config user.name "Jenkins"
                    git config user.email "jenkins@company.com"
                    git add DocGen/
                    git commit -m "docs: Update documentation [skip ci]" || exit 0
                    git push origin main
                '''
            }
        }
    }
}
```

---

## 📊 Projet avec plusieurs environnements

### Structure

```
project/
├── docgen.yaml           # Défaut
├── docgen.dev.yaml       # Développement
├── docgen.prod.yaml      # Production
└── docgen.ci.yaml        # CI/CD
```

### Configuration développement

```yaml
# docgen.dev.yaml
output_dir: docs-dev
exclude:
  - .git/
readme_target: output
enable_github_pages: false
enable_doxygen_block: false
```

### Configuration production

```yaml
# docgen.prod.yaml
output_dir: docs
exclude:
  - .git/
  - node_modules/
  - venv/
  - tests/
  - "*.test.*"
readme_target: output
enable_github_pages: true
enable_doxygen_block: true
```

### Utilisation

```bash
# Développement
docgen build --config docgen.dev.yaml

# Production
docgen build --config docgen.prod.yaml --force --doxygen

# CI
docgen build --config docgen.ci.yaml --force
```

---

## 🎯 Workflow avec pre-commit

### Installation

```bash
pip install pre-commit
```

### Configuration

Créez `.pre-commit-config.yaml` :

```yaml
repos:
  - repo: local
    hooks:
      - id: docgen
        name: Generate documentation
        entry: docgen build --force
        language: system
        pass_filenames: false
        stages: [commit]
```

### Activation

```bash
pre-commit install
```

Maintenant, à chaque commit, la documentation est automatiquement mise à jour !

---

## 🔄 Workflow avec Makefile

Créez `Makefile` :

```makefile
.PHONY: help init scan docs docs-dry docs-force clean

help:  ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init:  ## Initialiser DocGen
	docgen init

scan:  ## Scanner le projet
	docgen scan --format text

docs:  ## Générer la documentation
	docgen build

docs-dry:  ## Aperçu de la génération
	docgen build --dry-run

docs-force:  ## Générer en écrasant
	docgen build --force

docs-full:  ## Générer avec Doxygen
	docgen build --force --doxygen

clean:  ## Nettoyer la documentation
	rm -rf DocGen/

.DEFAULT_GOAL := help
```

### Utilisation

```bash
make help        # Afficher l'aide
make init        # Initialiser
make scan        # Scanner
make docs        # Générer
make docs-force  # Force update
make docs-full   # Avec Doxygen
make clean       # Nettoyer
```

---

## 📖 Workflow avec tox (Python)

Créez `tox.ini` :

```ini
[tox]
envlist = py311, docs, lint

[testenv:docs]
description = Generate documentation
deps =
    -e.
commands =
    docgen scan
    docgen build --force

[testenv:docs-check]
description = Check documentation
deps =
    -e.
commands =
    docgen build --dry-run

[testenv]
deps = pytest
commands = pytest
```

### Utilisation

```bash
tox -e docs        # Générer la documentation
tox -e docs-check  # Vérifier
```

---

## 💡 Conseils et bonnes pratiques

### 1. Documentation évolutive

```bash
# Première génération
docgen build

# Éditer manuellement les fichiers
# (ajouter des notes, personnaliser...)

# Mettre à jour uniquement les blocs auto
docgen build --force
```

Les sections manuelles sont préservées !

### 2. Validation avant commit

```bash
# Script pre-push
#!/bin/bash
docgen scan --format json > /dev/null || exit 1
docgen build --dry-run || exit 1
echo "Documentation OK ✓"
```

### 3. Documentation multi-formats

```bash
# Générer la doc
docgen build --force

# Convertir en PDF (avec pandoc)
pandoc DocGen/README.md -o docs/README.pdf

# Convertir en HTML statique
mkdocs build
```

### 4. Versioning de la documentation

```bash
# Tagger la documentation
git tag -a docs-v1.0 -m "Documentation v1.0"
git push origin docs-v1.0

# Archiver
tar -czf docs-v1.0.tar.gz DocGen/
```

---

## 📚 Ressources supplémentaires

- [Guide de démarrage](getting-started)
- [Référence des commandes](commands)
- [Configuration](configuration)
- [Dépôt GitHub](https://github.com/yourusername/DocGen)

---

## 🤝 Partager vos exemples

Vous avez un cas d'usage intéressant ? Partagez-le avec la communauté !

1. Forkez le projet
2. Ajoutez votre exemple dans `examples/`
3. Ouvrez une Pull Request

Nous serons ravis d'enrichir cette page avec vos contributions ! 🎉
