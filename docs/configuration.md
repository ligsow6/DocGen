---
layout: default
title: Configuration
nav_order: 4
description: "Guide complet de configuration de DocGen"
permalink: /configuration
---

# Configuration
{: .no_toc }

Guide complet pour personnaliser DocGen selon vos besoins.
{: .fs-6 .fw-300 }

## Table des matières
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 📄 Fichier de configuration

DocGen utilise un fichier YAML pour sa configuration, par défaut nommé `docgen.yaml` et placé à la racine du projet.

### Configuration par défaut

Lors de l'exécution de `docgen init`, le fichier suivant est créé :

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

---

## ⚙️ Options de configuration

### `output_dir`

**Type :** `string`  
**Défaut :** `DocGen`  
**Description :** Chemin du dossier où la documentation sera générée.

```yaml
# Exemples
output_dir: DocGen          # À la racine
output_dir: docs/api        # Sous-dossier
output_dir: ../docs         # Dossier parent
```

**Cas d'usage :**
- `DocGen` : Convention par défaut
- `docs` : Pour GitHub Pages activé sur `/docs`
- `.github/docs` : Organisation avec autres fichiers GitHub

---

### `exclude`

**Type :** `list[string]`  
**Défaut :** `[.git/, node_modules/, dist/, build/]`  
**Description :** Liste de patterns glob pour exclure des fichiers/dossiers de l'analyse.

```yaml
exclude:
  - .git/              # Dossier Git
  - node_modules/      # Dépendances Node.js
  - dist/              # Builds
  - build/             # Builds
  - venv/              # Environnements virtuels Python
  - .venv/
  - __pycache__/       # Cache Python
  - "*.pyc"            # Fichiers compilés Python
  - .env               # Variables d'environnement
  - "*.log"            # Fichiers de log
  - coverage/          # Rapports de couverture
  - .pytest_cache/     # Cache pytest
```

**Patterns supportés :**
- `folder/` : Dossier spécifique
- `*.ext` : Tous les fichiers avec une extension
- `**/pattern` : Récursif dans tous les sous-dossiers
- `folder/*.py` : Fichiers Python dans un dossier spécifique

**Exemples de configurations :**

#### Projet Python

```yaml
exclude:
  - .git/
  - venv/
  - .venv/
  - __pycache__/
  - "*.pyc"
  - .pytest_cache/
  - htmlcov/
  - dist/
  - build/
  - "*.egg-info/"
```

#### Projet Node.js

```yaml
exclude:
  - .git/
  - node_modules/
  - dist/
  - build/
  - coverage/
  - .next/
  - out/
  - "*.log"
```

#### Projet multi-langue

```yaml
exclude:
  - .git/
  - node_modules/
  - venv/
  - dist/
  - build/
  - target/        # Maven (Java)
  - vendor/        # Composer (PHP)
  - "*.log"
```

---

### `readme_target`

**Type :** `string`  
**Défaut :** `output`  
**Valeurs possibles :** `output`, `root`  
**Description :** Emplacement où générer le fichier README principal.

```yaml
# Générer dans le dossier de sortie
readme_target: output
# → DocGen/README.md

# Générer à la racine du projet
readme_target: root
# → README.md (à la racine)
```

**Cas d'usage :**

- **`output`** (recommandé) :
  - Sépare la documentation générée du code source
  - Permet d'avoir un README manuel à la racine
  - Idéal pour les projets avec documentation séparée

- **`root`** :
  - README principal généré automatiquement
  - Simplifie la structure pour petits projets
  - Attention : écrasera le README existant avec `--force`

---

### `enable_github_pages`

**Type :** `boolean`  
**Défaut :** `true`  
**Description :** Active la génération de fichiers pour GitHub Pages.

```yaml
# Activer GitHub Pages
enable_github_pages: true

# Désactiver
enable_github_pages: false
```

**Quand activé :**
- Génère un fichier `index.md` pour la page d'accueil
- Structure la documentation pour Jekyll
- Ajoute des métadonnées frontmatter

**Configuration GitHub Pages :**

1. Activez GitHub Pages dans les paramètres du dépôt
2. Source : `main` branch, dossier `/DocGen` (ou votre `output_dir`)
3. Thème : Choisissez un thème Jekyll ou utilisez un `_config.yml` custom

---

### `enable_doxygen_block`

**Type :** `string | boolean`  
**Défaut :** `auto`  
**Valeurs possibles :** `auto`, `true`, `false`  
**Description :** Contrôle l'intégration avec Doxygen.

```yaml
# Détection automatique (recommandé)
enable_doxygen_block: auto

# Toujours activer
enable_doxygen_block: true

# Toujours désactiver
enable_doxygen_block: false
```

**Comportement :**

- **`auto`** : Détecte automatiquement si un `Doxyfile` existe
- **`true`** : Force l'intégration Doxygen (ajoute des blocs dans la doc)
- **`false`** : Désactive complètement Doxygen

**Prérequis pour Doxygen :**
- Fichier `Doxyfile` à la racine du projet
- Doxygen installé sur le système
- Utiliser l'option `--doxygen` avec `docgen build`

---

## 📋 Exemples de configurations complètes

### Projet Python simple

```yaml
output_dir: docs
exclude:
  - .git/
  - venv/
  - __pycache__/
  - "*.pyc"
  - dist/
  - build/
readme_target: output
enable_github_pages: true
enable_doxygen_block: false
```

### Projet Node.js/TypeScript

```yaml
output_dir: DocGen
exclude:
  - .git/
  - node_modules/
  - dist/
  - build/
  - coverage/
  - .next/
  - "*.log"
readme_target: root
enable_github_pages: true
enable_doxygen_block: false
```

### Projet C++ avec Doxygen

```yaml
output_dir: docs/api
exclude:
  - .git/
  - build/
  - cmake-build-*/
  - "*.o"
  - "*.a"
  - "*.so"
readme_target: output
enable_github_pages: true
enable_doxygen_block: true
```

### Monorepo multi-langages

```yaml
output_dir: documentation
exclude:
  - .git/
  - "**/node_modules/"
  - "**/venv/"
  - "**/dist/"
  - "**/build/"
  - "**/target/"
  - "**/__pycache__/"
  - "*.log"
readme_target: output
enable_github_pages: true
enable_doxygen_block: auto
```

### Projet avec structure complexe

```yaml
output_dir: .github/documentation
exclude:
  # Version control
  - .git/
  - .svn/
  
  # Dependencies
  - node_modules/
  - venv/
  - vendor/
  - target/
  
  # Build outputs
  - dist/
  - build/
  - out/
  - bin/
  
  # Caches
  - __pycache__/
  - .pytest_cache/
  - .mypy_cache/
  - .ruff_cache/
  - "*.pyc"
  
  # IDE
  - .vscode/
  - .idea/
  - "*.swp"
  
  # OS
  - .DS_Store
  - Thumbs.db
  
  # Logs & temporary
  - "*.log"
  - tmp/
  - temp/
  
  # Sensitive
  - .env
  - .env.local
  - secrets/

readme_target: output
enable_github_pages: true
enable_doxygen_block: auto
```

---

## 🎯 Configurations par cas d'usage

### Pour un projet open-source

```yaml
output_dir: docs
exclude:
  - .git/
  - node_modules/
  - venv/
  - dist/
  - build/
readme_target: root        # README à la racine pour GitHub
enable_github_pages: true  # Documentation hébergée
enable_doxygen_block: auto
```

### Pour un projet d'entreprise

```yaml
output_dir: documentation/technical
exclude:
  - .git/
  - node_modules/
  - venv/
  - dist/
  - build/
  - confidential/
  - internal/
readme_target: output
enable_github_pages: false  # Hébergement interne
enable_doxygen_block: true
```

### Pour un projet de bibliothèque

```yaml
output_dir: docs/api
exclude:
  - .git/
  - venv/
  - dist/
  - build/
  - examples/
  - tests/
readme_target: output
enable_github_pages: true
enable_doxygen_block: true  # Documentation API détaillée
```

### Pour un micro-service

```yaml
output_dir: DocGen
exclude:
  - .git/
  - venv/
  - __pycache__/
  - "*.pyc"
readme_target: output
enable_github_pages: false  # Pas besoin de GitHub Pages
enable_doxygen_block: false
```

---

## 🔍 Validation de la configuration

### Vérifier votre configuration

```bash
# Scanner avec configuration actuelle
docgen scan

# Tester avec une config spécifique
docgen scan --config test-config.yaml

# Dry-run pour voir les fichiers générés
docgen build --dry-run
```

### Erreurs courantes

#### Configuration invalide

```bash
# Erreur
Error: Unknown config keys: output_directory

# Solution : utiliser le bon nom de clé
output_dir: DocGen
```

#### YAML invalide

```bash
# Erreur
Error: Invalid YAML in config

# Vérifier l'indentation et la syntaxe
```

#### Chemins invalides

```bash
# Erreur
Error: Output directory cannot be absolute

# Solution : utiliser un chemin relatif
output_dir: docs        # ✅ Bon
output_dir: /tmp/docs   # ❌ Mauvais
```

---

## 🛠️ Configuration avancée

### Variables d'environnement

DocGen respecte certaines variables d'environnement :

```bash
# Désactiver les couleurs
export NO_COLOR=1

# Forcer les couleurs
export FORCE_COLOR=1
```

### Configurations multiples

Vous pouvez avoir plusieurs configurations pour différents environnements :

```bash
# Structure
project/
├── docgen.yaml              # Config par défaut
├── docgen.prod.yaml         # Config production
└── docgen.dev.yaml          # Config développement

# Utilisation
docgen build --config docgen.prod.yaml
```

**Exemple `docgen.dev.yaml` :**

```yaml
output_dir: docs-dev
exclude:
  - .git/
readme_target: output
enable_github_pages: false
enable_doxygen_block: false
```

**Exemple `docgen.prod.yaml` :**

```yaml
output_dir: docs
exclude:
  - .git/
  - node_modules/
  - venv/
  - dist/
  - build/
  - tests/
  - "*.test.js"
  - "test_*.py"
readme_target: output
enable_github_pages: true
enable_doxygen_block: true
```

---

## 📚 Bonnes pratiques

### ✅ À faire

- **Commiter `docgen.yaml`** dans le dépôt pour partager la configuration
- **Utiliser des chemins relatifs** pour `output_dir`
- **Documenter les exclusions** si elles sont non-standard
- **Tester avec `--dry-run`** avant de générer
- **Versionner la config** avec le code

### ❌ À éviter

- Chemins absolus dans la configuration
- Exclure trop de fichiers (peut manquer des détections)
- Modifier la config sans tester
- Chemins sensibles à la casse sur Windows/Mac

---

## 💡 Astuces

### Ignorer la documentation générée dans Git

```bash
# .gitignore
DocGen/
!DocGen/.gitkeep

# Ou commiter la documentation
# (Ne rien ajouter dans .gitignore)
```

### Template de configuration

Créez un template réutilisable :

```yaml
# docgen.template.yaml
output_dir: ${OUTPUT_DIR:-DocGen}
exclude:
  - .git/
  - ${DEPENDENCIES_DIR:-node_modules}/
readme_target: ${README_TARGET:-output}
enable_github_pages: ${ENABLE_PAGES:-true}
enable_doxygen_block: auto
```

---

## 📚 Voir aussi

- [Commandes](commands) : Référence des commandes CLI
- [Exemples](examples) : Cas d'usage concrets
- [Guide de démarrage](getting-started) : Premiers pas
