# DocGen

DocGen est un CLI qui genere une documentation Markdown standardisee a partir d'un depot Git local.
Il detecte la stack, propose des commandes usuelles, puis met a jour uniquement les sections gerees.

## Installation (dev)

- Requires Python 3.11+
- Dependency management: `pyproject.toml` with setuptools + pip

Install in editable mode:

```
python -m pip install -e ".[dev]"
```

Run the CLI:

```
docgen --help
python -m docgen --help
```

Initialize configuration:

```
docgen init
```

Run scan/build:

```
docgen scan --format text
docgen scan --format json

docgen build --dry-run
docgen build
docgen build --force
```

## Commandes

- `docgen init` : cree `docgen.yaml` avec les defaults.
- `docgen scan` : analyse le depot (stacks, commandes, CI).
- `docgen build` : genere/actualise README, ARCHITECTURE et index.
- `--debug` : affiche les details d'erreur (stacktrace).

## Idempotence & sections gerees

## Idempotence & sections gerees

DocGen gere uniquement des sections encadrees par des marqueurs HTML :

```
<!-- DOCGEN:START summary -->
... contenu gere ...
<!-- DOCGEN:END summary -->
```

Tout contenu hors des marqueurs est preserve. Relancer `docgen build` met a jour
uniquement les sections gerees, sans ecraser les notes manuelles.

## Exemple avant / apres

Avant (manuel) :

```
# Mon Projet

Mes notes personnelles.
```

Apres `docgen build` :

```
# Mon Projet

Mes notes personnelles.

<!-- DOCGEN:START summary -->
## Summary
Documentation generee automatiquement a partir du depot.
<!-- DOCGEN:END summary -->
```

## Limites connues

- Pas de publication automatique (GitHub Pages/Doxygen non declenches).
- Pas d'analyse profonde du code (scan base sur fichiers et configs).
- Pas de mise en page personnalisee hors templates.

## Spec

Voir `docs/spec.md` pour le contrat complet.
