# Examples

## Mini repo (avant DocGen)

Dossier: `examples/mini_repo/`
- Pas de documentation.
- Contient un mini projet Python (pyproject + requirements + src + tests).

## Apres DocGen

Dossier: `examples/mini_repo_after/DocGen/`
- `README.md`
- `ARCHITECTURE.md`

## Commandes executees (exemple)

```
docgen scan --repo examples/mini_repo --format text
```

Resultat attendu (resume):
- Stack: python
- Commandes: pytest, ruff check .

```
docgen build --repo examples/mini_repo --force
```

Resultat attendu:
- `examples/mini_repo/DocGen/README.md`
- `examples/mini_repo/DocGen/ARCHITECTURE.md`
- `examples/mini_repo/DocGen/index.md`
