# Quietstack

Site de contenu sur l'ergonomie du télétravail (bureaux assis-debout),
avec publication d'articles **entièrement automatisée**.

## Comment ça marche

- Tous les articles sont déjà écrits, dans `content/articles/` (fichiers `.md`).
- Chaque article a une date de publication programmée dans son en-tête.
- Un script (`scripts/build.py`) génère le site dans `docs/` en ne publiant
  que les articles dont la date est passée.
- Une GitHub Action (`.github/workflows/build-and-deploy.yml`) exécute ce
  script **tous les jours automatiquement** et republie le site si un
  nouvel article doit apparaître. Tu n'as rien à déclencher toi-même.

Concrètement : une fois la mise en place terminée, un nouvel article
apparaît sur ton site tous les 4 jours environ, sans aucune action de
ta part.

## Mise en place (à faire une seule fois)

### Autoriser les Actions à écrire dans le repository

- Va dans **Settings** (du repository) → **Actions** → **General**
- Descends jusqu'à **Workflow permissions**
- Sélectionne **Read and write permissions**
- **Save**

Sans cette étape, l'automatisation ne pourra pas publier les mises à jour.

### Activer GitHub Pages

- Toujours dans **Settings** → **Pages**
- Source : **Deploy from a branch**
- Branch : `main`, dossier `/docs`
- **Save**

Ton site sera en ligne à une adresse du type :
`https://quietstack-cmd.github.io/quietstack/`

### Lancer le premier build

Va dans l'onglet **Actions** du repository → clique sur le workflow
**Build & publish Quietstack** → **Run workflow** → **Run workflow**.

Ça déclenche la première génération manuellement. Après ça, tout est automatique.

## Ajouter des articles plus tard

Pour ajouter de nouveaux articles au stock, dépose simplement un nouveau
fichier `.md` dans `content/articles/`, avec le même format d'en-tête que
les articles existants (title, slug, date, category, read_time, excerpt).
Il sera publié automatiquement à la date indiquée.

## Monétisation

Le site est prêt pour l'affiliation (mention légale déjà présente en bas
de chaque article). Pour ajouter tes propres liens affiliés :
1. Crée un compte sur Amazon Partenaires (ou un autre programme)
2. Remplace les mentions de produits dans les articles par des liens
   affiliés réels, directement dans les fichiers `.md`
