---
layout: default
title: Accueil
nav_order: 1
description: "DocGen - Générateur automatique de documentation pour vos projets Git"
permalink: /
---

# DocGen
{: .fs-9 }

Générez automatiquement une documentation standardisée et professionnelle pour vos projets Git.
{: .fs-6 .fw-300 }

[Commencer maintenant](#installation){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Voir sur GitHub](https://github.com/yourusername/DocGen){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## ✨ Pourquoi DocGen ?

DocGen simplifie la création et la maintenance de documentation de projet en analysant automatiquement votre codebase et en générant des documents Markdown structurés.

### 🎯 Fonctionnalités principales

<div class="feature-grid">

**🔍 Détection automatique**
{: .text-delta }
Identifie automatiquement les technologies utilisées : Python, Node.js, Docker, Java, et plus encore.

**⚡ Rapide et efficace**
{: .text-delta }
Génère une documentation complète en quelques secondes sans intervention manuelle.

**📝 Blocs intelligents**
{: .text-delta }
Préserve vos notes manuelles tout en mettant à jour les sections générées automatiquement.

**🎨 Personnalisable**
{: .text-delta }
Configuration flexible via `docgen.yaml` pour adapter l'outil à vos besoins.

**🔧 Support Doxygen**
{: .text-delta }
Intégration optionnelle avec Doxygen pour la documentation de code détaillée.

**📦 GitHub Pages**
{: .text-delta }
Génération automatique de sites de documentation hébergés sur GitHub Pages.

</div>

---

## 🚀 Installation

### Prérequis

- Python >= 3.11
- pip

### Installation depuis le code source

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/DocGen.git
cd DocGen

# Installer avec pip
pip install -e .
```

---

## ⚡ Démarrage rapide

### 1. Initialiser DocGen

```bash
cd /mon/projet
docgen init
```

Cette commande crée :
- Un fichier `docgen.yaml` pour la configuration
- Un dossier `DocGen/` avec des templates de documentation

### 2. Scanner votre projet

```bash
docgen scan
```

Affiche les technologies détectées, les commandes disponibles, et la structure du projet.

### 3. Générer la documentation

```bash
docgen build
```

Votre documentation est créée dans le dossier `DocGen/` ! 🎉

---

## 📚 Documentation

<div class="card-grid">

[**Guide de démarrage**](getting-started)
{: .fs-5 }
Installez et configurez DocGen en quelques minutes
{: .fs-3 .text-grey-dk-000 }

[**Référence des commandes**](commands)
{: .fs-5 }
Documentation complète de toutes les commandes CLI
{: .fs-3 .text-grey-dk-000 }

[**Configuration**](configuration)
{: .fs-5 }
Personnalisez DocGen selon vos besoins
{: .fs-3 .text-grey-dk-000 }

[**Exemples**](examples)
{: .fs-5 }
Découvrez des cas d'usage concrets
{: .fs-3 .text-grey-dk-000 }

</div>

---

## 🎯 Exemple d'utilisation

```bash
# Naviguer vers votre projet
cd /mon/super/projet

# Initialiser DocGen
docgen init

# Scanner le projet (optionnel, pour voir ce qui sera détecté)
docgen scan --format text

# Générer la documentation
docgen build --force

# Votre documentation est prête !
ls DocGen/
# Output: README.md  ARCHITECTURE.md  index.md
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](https://github.com/yourusername/DocGen/blob/main/LICENSE) pour plus de détails.

---

## 💬 Support

Besoin d'aide ? Plusieurs options s'offrent à vous :

- 📖 [Documentation complète](getting-started)
- 🐛 [Signaler un bug](https://github.com/yourusername/DocGen/issues)
- 💡 [Proposer une fonctionnalité](https://github.com/yourusername/DocGen/issues)
- 💬 [Discussions](https://github.com/yourusername/DocGen/discussions)

---

<div class="footer-banner">
Fait avec ❤️ par la communauté DocGen
</div>
