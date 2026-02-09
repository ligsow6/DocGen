---
layout: default
title: Guide de démarrage
nav_order: 2
description: "Installez et configurez DocGen rapidement"
permalink: /getting-started
---

# Guide de démarrage
{: .no_toc }

Ce guide vous accompagne pas à pas dans l'installation et la première utilisation de DocGen.
{: .fs-6 .fw-300 }

## Table des matières
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.11 ou supérieur** installé
- **pip** (gestionnaire de paquets Python)
- **Git** configuré sur votre machine
- Un projet Git existant à documenter

### Vérifier votre installation

```bash
# Vérifier Python
python --version
# Output attendu: Python 3.11.x ou supérieur

# Vérifier pip
pip --version
# Output attendu: pip 23.x.x ou supérieur

# Vérifier Git
git --version
# Output attendu: git version 2.x.x
```

---

## 💾 Installation

### Option 1 : Installation depuis le code source (recommandé)

```bash
# 1. Cloner le dépôt
git clone https://github.com/yourusername/DocGen.git
cd DocGen

# 2. Installer en mode éditable (développement)
pip install -e .

# 3. Vérifier l'installation
docgen --help
```

### Option 2 : Installation depuis PyPI (future)

```bash
# Quand disponible sur PyPI
pip install docgen-cli

# Vérifier l'installation
docgen --help
```

### Installation des dépendances de développement

Si vous souhaitez contribuer au projet :

```bash
# Installer avec les dépendances de développement
pip install -e ".[dev]"

# Lancer les tests
pytest
```

---

## 🚀 Premier usage

### Étape 1 : Initialiser DocGen dans votre projet

Naviguez vers votre projet et initialisez DocGen :

```bash
cd /chemin/vers/votre/projet
docgen init
```

**Résultat :**
```
Config created: /chemin/vers/votre/projet/docgen.yaml
Output dir: /chemin/vers/votre/projet/DocGen
Exclude: .git/, node_modules/, dist/, build/
Created: /chemin/vers/votre/projet/DocGen/README.md
Created: /chemin/vers/votre/projet/DocGen/ARCHITECTURE.md
```

Cette commande crée :
- `docgen.yaml` : fichier de configuration
- `DocGen/README.md` : template de documentation principale
- `DocGen/ARCHITECTURE.md` : template de documentation d'architecture

### Étape 2 : Scanner votre projet

Avant de générer la documentation, vous pouvez scanner votre projet pour voir ce que DocGen détecte :

```bash
docgen scan
```

**Exemple de sortie :**

```
Project: MonProjet
Repo: /chemin/vers/votre/projet
Output dir: DocGen
Exclude: .git/, node_modules/, dist/, build/

╭─────────── Stacks ────────────╮
│ Name   Confidence  Evidence   │
├───────────────────────────────┤
│ python    1.00    pyproject.toml, requirements.txt │
│ docker    0.80    Dockerfile   │
╰───────────────────────────────╯

╭────────── Commands ───────────╮
│ Type   Command               │
├───────────────────────────────┤
│ run    python -m app          │
│ test   pytest                 │
│ lint   ruff check .           │
│ build  python -m build        │
│ format ruff format .          │
╰───────────────────────────────╯

Detected files:
- pyproject.toml (config)
- requirements.txt (config)
- Dockerfile (docker)
CI: GitHub Actions
Package manager: pip
```

### Étape 3 : Générer la documentation

```bash
docgen build
```

**Résultat :**
```
Files prepared:
- DocGen/README.md
- DocGen/ARCHITECTURE.md
- DocGen/index.md

Sections:
- README.md:
  - replaced: readme.summary, readme.stack, readme.commands
- ARCHITECTURE.md:
  - replaced: arch.overview, arch.components
```

---

## 📂 Structure générée

Après l'exécution de `docgen build`, voici la structure créée :

```
votre-projet/
├── docgen.yaml                 # Configuration DocGen
├── DocGen/                     # Dossier de documentation
│   ├── README.md              # Documentation principale
│   ├── ARCHITECTURE.md        # Documentation d'architecture
│   └── index.md               # Page d'index (GitHub Pages)
├── src/                        # Votre code source
└── ...
```

---

## 🎯 Workflow recommandé

### Workflow de base

```bash
# 1. Initialiser (une seule fois)
docgen init

# 2. Développer votre projet
# ... écrire du code ...

# 3. Mettre à jour la documentation
docgen build --force

# 4. Commiter
git add DocGen/ docgen.yaml
git commit -m "docs: Update documentation"
```

### Workflow avec aperçu

```bash
# 1. Scanner pour vérifier la détection
docgen scan --format text

# 2. Aperçu sans écrire les fichiers
docgen build --dry-run

# 3. Si tout est OK, générer
docgen build --force
```

### Workflow avec options avancées

```bash
# Générer avec Doxygen (si Doxyfile existe)
docgen build --doxygen

# Scanner au format JSON pour l'automatisation
docgen scan --format json > project-info.json

# Utiliser une configuration personnalisée
docgen build --config custom-config.yaml
```

---

## ⚙️ Configuration initiale

Le fichier `docgen.yaml` créé par `docgen init` contient une configuration par défaut :

```yaml
output_dir: DocGen
exclude:
  - .git/
  - node_modules/
  - dist/
  - build/
readme_target: output
enable_github_pages: true
enable_doxygen_block: auto
```

Vous pouvez le personnaliser selon vos besoins. Consultez la page [Configuration](configuration) pour plus de détails.

---

## ✅ Vérification de l'installation

Pour vérifier que tout fonctionne correctement :

```bash
# 1. Vérifier la version
docgen --help

# 2. Créer un projet de test
mkdir test-docgen
cd test-docgen
git init
echo "# Test" > README.md
echo "print('Hello')" > main.py

# 3. Initialiser et générer
docgen init
docgen scan
docgen build

# 4. Vérifier le résultat
ls DocGen/
# Output attendu: README.md  ARCHITECTURE.md  index.md
```

---

## 🐛 Résolution de problèmes

### Erreur : "Command not found: docgen"

**Solution :**
```bash
# Vérifier que le package est installé
pip list | grep docgen

# Réinstaller si nécessaire
pip install -e /chemin/vers/DocGen
```

### Erreur : "Config file not found"

**Solution :**
```bash
# Créer le fichier de configuration
docgen init

# Ou spécifier un chemin custom
docgen build --config /chemin/vers/docgen.yaml
```

### Les fichiers ne sont pas mis à jour

**Solution :**
```bash
# Utiliser l'option --force pour écraser
docgen build --force
```

### Activer les logs de debug

```bash
# Voir plus de détails
docgen --verbose build

# Voir les stack traces complètes
docgen --debug build
```

---

## 📚 Prochaines étapes

Maintenant que DocGen est installé et configuré :

1. 📖 Explorez la [référence des commandes](commands)
2. ⚙️ Découvrez les [options de configuration](configuration)
3. 🎯 Consultez les [exemples d'utilisation](examples)
4. 🤝 [Contribuez au projet](https://github.com/yourusername/DocGen)

---

## 💡 Conseils

- **Intégrez DocGen dans votre CI/CD** pour maintenir la documentation à jour automatiquement
- **Committez le fichier `docgen.yaml`** pour partager la configuration avec votre équipe
- **Utilisez `--dry-run`** pour prévisualiser les changements avant de générer
- **Personnalisez les templates** dans `DocGen/` en ajoutant vos propres sections
