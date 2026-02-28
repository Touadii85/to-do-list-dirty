#!/bin/bash

# Vérification du paramètre
if [ -z "$1" ]; then
  echo "Usage: ./build.sh version=X.Y.Z"
  exit 1
fi

# Extraction de la version
VERSION=$(echo $1 | cut -d'=' -f2)

if [ -z "$VERSION" ]; then
  echo "Version invalide."
  exit 1
fi

echo "Nouvelle version : $VERSION"

# Mise à jour de la variable dans settings.py
sed -i "s/^APP_VERSION = .*/APP_VERSION = \"$VERSION\"/" todo/settings.py

# Ajout et commit de la modification
git add todo/settings.py
git commit -m "chore: bump version to $VERSION"

# Création du tag
git tag $VERSION

# Génération de l'archive
git archive --format=zip --prefix=todolist-$VERSION/ -o todolist-$VERSION.zip $VERSION

echo "Build terminé : todolist-$VERSION.zip"