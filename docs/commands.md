---
layout: default
title: Référence des commandes
nav_order: 3
description: "Documentation complète de toutes les commandes DocGen"
permalink: /commands
---

# Référence des commandes
{: .no_toc }

Documentation complète de toutes les commandes et options disponibles dans DocGen.
{: .fs-6 .fw-300 }

## Table des matières
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 🎛️ Options globales

Ces options sont disponibles pour toutes les commandes :

| Option | Alias | Description |
|:-------|:------|:------------|
| `--verbose` | `-v` | Active les logs détaillés pour le débogage |
| `--debug` | - | Affiche les stack traces complètes en cas d'erreur |
| `--help` | - | Affiche l'aide de la commande |

### Exemples

```bash
# Activer les logs verbeux
docgen --verbose build

# Mode debug avec stack traces
docgen --debug scan

# Aide globale
docgen --help
```

---

## 📝 Commande `init`

Initialise DocGen dans un projet en créant le fichier de configuration et les templates de documentation.

### Syntaxe

```bash
docgen init [OPTIONS]
```

### Options

| Option | Alias | Type | Défaut | Description |
|:-------|:------|:-----|:-------|:------------|
| `--repo` | `-r` | PATH | `.` (répertoire courant) | Chemin du dépôt à initialiser |
| `--config` | `-c` | PATH | `docgen.yaml` | Chemin du fichier de configuration |

### Comportement

1. Crée un fichier `docgen.yaml` avec la configuration par défaut
2. Crée le dossier `DocGen/` (configurable)
3. Génère les templates `README.md` et `ARCHITECTURE.md`
4. N'écrase pas les fichiers existants

### Exemples

```bash
# Initialiser dans le répertoire courant
docgen init

# Initialiser un projet spécifique
docgen init --repo /chemin/vers/projet

# Utiliser un nom de config personnalisé
docgen init --config custom-config.yaml

# Initialiser avec logs verbeux
docgen --verbose init --repo ~/projects/mon-app
```

### Sortie

```
Config created: /projet/docgen.yaml
Output dir: /projet/DocGen
Exclude: .git/, node_modules/, dist/, build/
Created: /projet/DocGen/README.md
Created: /projet/DocGen/ARCHITECTURE.md
```

### Codes de sortie

| Code | Signification |
|:-----|:--------------|
| `0` | Succès |
| `1` | Erreur de configuration |
| `2` | Erreur d'IO (permissions, disque plein, etc.) |
| `3` | Utilisation incorrecte |

---

## 🔍 Commande `scan`

Analyse le dépôt et affiche les informations détectées sans générer de documentation.

### Syntaxe

```bash
docgen scan [OPTIONS]
```

### Options

| Option | Alias | Type | Défaut | Description |
|:-------|:------|:-----|:-------|:------------|
| `--repo` | `-r` | PATH | `.` | Chemin du dépôt à scanner |
| `--config` | `-c` | PATH | `docgen.yaml` | Chemin du fichier de configuration |
| `--format` | `-f` | text\|json | `text` | Format de sortie |

### Informations détectées

- **Nom du projet**
- **Technologies/stacks** avec niveau de confiance (0.0 à 1.0)
- **Commandes disponibles** : run, test, lint, build, format
- **Fichiers de configuration** détectés
- **CI/CD** : GitHub Actions, GitLab CI, Jenkins, etc.
- **Gestionnaire de packages** : pip, npm, yarn, maven, etc.
- **Outils Python** : pytest, ruff, mypy, black, etc.
- **Structure du projet**
- **Avertissements** éventuels

### Exemples

#### Format texte (avec Rich)

```bash
docgen scan
```

**Sortie :**

```
Project: MonProjet
Repo: /home/user/MonProjet
Output dir: DocGen
Exclude: .git/, node_modules/, dist/, build/

╭───────── Stacks ──────────╮
│ Name     Confidence  Evidence │
├───────────────────────────────┤
│ python   1.00        pyproject.toml │
│ node     0.90        package.json │
│ docker   0.80        Dockerfile │
╰───────────────────────────────╯

╭──────── Commands ─────────╮
│ Type   Command            │
├───────────────────────────┤
│ run    npm start          │
│ test   pytest && npm test │
│ lint   ruff check .       │
│ build  npm run build      │
│ format ruff format .      │
╰───────────────────────────╯

Detected files:
- pyproject.toml (config)
- package.json (config)
- Dockerfile (docker)
- docker-compose.yml (docker)

CI: GitHub Actions
Package manager: pip, npm
Python tooling: pytest, ruff
```

#### Format JSON

```bash
docgen scan --format json
```

**Sortie :**

```json
{
  "project_name": "MonProjet",
  "repo_root": "/home/user/MonProjet",
  "stacks": [
    {
      "name": "python",
      "confidence": 1.0,
      "evidence": ["pyproject.toml", "requirements.txt"]
    }
  ],
  "commands": {
    "run": "python -m app",
    "test": "pytest",
    "lint": "ruff check .",
    "build": "python -m build",
    "format": "ruff format ."
  },
  "files_detected": [
    {"path": "pyproject.toml", "type": "config"}
  ],
  "ci": ["github"],
  "package_manager": "pip",
  "python_tooling": "pytest,ruff",
  "warnings": []
}
```

### Cas d'usage

- **Vérifier la détection** avant de générer la documentation
- **Débogage** : comprendre ce que DocGen voit dans votre projet
- **Automatisation** : utiliser le format JSON dans des scripts CI/CD
- **Audit** : obtenir un aperçu rapide des technologies d'un projet

### Exemples avancés

```bash
# Scanner un projet externe
docgen scan --repo ~/projects/autre-projet

# Sortie JSON pour traitement
docgen scan --format json | jq '.stacks[].name'

# Scanner avec configuration personnalisée
docgen scan --config .docgen/config.yaml

# Scanner avec logs verbeux
docgen --verbose scan --format text
```

---

## 🏗️ Commande `build`

Génère la documentation complète du projet.

### Syntaxe

```bash
docgen build [OPTIONS]
```

### Options

| Option | Alias | Type | Défaut | Description |
|:-------|:------|:-----|:-------|:------------|
| `--repo` | `-r` | PATH | `.` | Chemin du dépôt |
| `--config` | `-c` | PATH | `docgen.yaml` | Chemin du fichier de configuration |
| `--dry-run` | - | flag | `false` | Aperçu sans écrire les fichiers |
| `--force` | - | flag | `false` | Écraser les fichiers existants |
| `--doxygen` | - | flag | `false` | Exécuter Doxygen si un Doxyfile existe |

### Comportement

1. **Scan** du projet pour détecter les technologies
2. **Lecture** des templates existants dans le dossier de sortie
3. **Mise à jour** des blocs DocGen (entre `<!-- DOCGEN:BEGIN -->` et `<!-- DOCGEN:END -->`)
4. **Préservation** des sections manuelles
5. **Génération** de fichiers supplémentaires (index.md pour GitHub Pages)
6. **Exécution** optionnelle de Doxygen

### Blocs DocGen

Les fichiers générés contiennent des blocs spéciaux qui peuvent être mis à jour automatiquement :

```markdown
<!-- DOCGEN:BEGIN id="readme.summary" -->
> Generated by DocGen. Do not edit this block manually.

Contenu généré automatiquement
<!-- DOCGEN:END id="readme.summary" -->
```

**Blocs disponibles :**

#### README.md
- `readme.summary` : Résumé du projet
- `readme.stack` : Technologies détectées
- `readme.commands` : Commandes disponibles
- `readme.documentation` : Liens vers la documentation

#### ARCHITECTURE.md
- `arch.overview` : Vue d'ensemble de l'architecture
- `arch.components` : Composants principaux
- `arch.data_flow` : Flux de données
- `arch.deployment` : Déploiement

### Exemples

#### Génération simple

```bash
docgen build
```

#### Aperçu avant génération

```bash
# Voir ce qui serait généré
docgen build --dry-run
```

**Sortie :**
```
Dry run. Files that would be generated:
- DocGen/README.md
- DocGen/ARCHITECTURE.md
- DocGen/index.md
```

#### Écraser les fichiers existants

```bash
# Force la réécriture des blocs
docgen build --force
```

#### Avec Doxygen

```bash
# Génère la doc + exécute Doxygen
docgen build --doxygen
```

**Prérequis :** Un fichier `Doxyfile` doit exister à la racine du projet.

#### Projet externe

```bash
# Générer pour un autre projet
docgen build --repo /chemin/vers/autre/projet
```

#### Configuration personnalisée

```bash
# Utiliser une config custom
docgen build --config configs/prod.yaml --force
```

### Sortie

```
Files prepared:
- DocGen/README.md
- DocGen/ARCHITECTURE.md
- DocGen/index.md

Sections:
- README.md:
  - created
  - replaced: readme.summary, readme.stack, readme.commands
  - unchanged: readme.documentation
- ARCHITECTURE.md:
  - replaced: arch.overview, arch.components
  - unchanged: arch.data_flow, arch.deployment
- index.md:
  - created

Doxygen: ran using Doxyfile
```

### Rapport de génération

Pour chaque fichier, DocGen affiche :
- ✅ **created** : Fichier nouvellement créé
- ✅ **overwritten** : Fichier existant écrasé (avec `--force`)
- 🔄 **added** : Nouveaux blocs ajoutés
- 🔄 **replaced** : Blocs mis à jour
- ⏭️ **unchanged** : Blocs inchangés

### Exemples de workflows

#### Workflow de base

```bash
# 1. Première génération
docgen build

# 2. Éditer manuellement les fichiers
# (ajouter des notes, personnaliser...)

# 3. Mettre à jour les blocs auto-générés
docgen build --force
```

#### Workflow avec validation

```bash
# 1. Scanner d'abord
docgen scan

# 2. Dry-run pour vérifier
docgen build --dry-run

# 3. Si OK, générer
docgen build --force
```

#### Workflow CI/CD

```bash
# Dans votre pipeline
docgen build --force
git add DocGen/
git commit -m "docs: Update auto-generated documentation"
git push
```

---

## 🔧 Combinaisons courantes

### Initialiser un nouveau projet

```bash
docgen init && docgen scan && docgen build
```

### Mise à jour complète de la documentation

```bash
docgen scan --format text
docgen build --force --doxygen
```

### Validation avant commit

```bash
docgen build --dry-run
docgen scan --format json > project-scan.json
```

### Debug complet

```bash
docgen --debug --verbose scan
docgen --debug --verbose build --dry-run
```

---

## 📊 Codes de sortie

Tous les codes de sortie utilisés par DocGen :

| Code | Nom | Description |
|:-----|:----|:------------|
| `0` | SUCCESS | Commande exécutée avec succès |
| `1` | CONFIG_ERROR | Erreur de configuration (fichier invalide, etc.) |
| `2` | IO_ERROR | Erreur d'entrée/sortie (permissions, disque, etc.) |
| `3` | USAGE_ERROR | Utilisation incorrecte de la commande |
| `99` | UNEXPECTED | Erreur inattendue |

---

## 💡 Astuces

### Alias Shell

Ajoutez ces alias dans votre `.bashrc` ou `.zshrc` :

```bash
alias dgi='docgen init'
alias dgs='docgen scan'
alias dgb='docgen build --force'
alias dgd='docgen build --dry-run'
```

### Scripts CI/CD

#### GitHub Actions

```yaml
- name: Generate documentation
  run: |
    pip install -e .
    docgen build --force
    git config user.name "DocGen Bot"
    git config user.email "bot@docgen.io"
    git add DocGen/
    git commit -m "docs: Update documentation [skip ci]" || exit 0
    git push
```

#### GitLab CI

```yaml
generate_docs:
  script:
    - pip install -e .
    - docgen build --force
    - git add DocGen/
    - git commit -m "docs: Update documentation" || exit 0
    - git push origin $CI_COMMIT_REF_NAME
```

### Makefile

```makefile
.PHONY: docs docs-scan docs-dry

docs:
	docgen build --force

docs-scan:
	docgen scan --format text

docs-dry:
	docgen build --dry-run
```

---

## 📚 Voir aussi

- [Configuration](configuration) : Personnaliser DocGen
- [Exemples](examples) : Cas d'usage concrets
- [Guide de démarrage](getting-started) : Premiers pas
