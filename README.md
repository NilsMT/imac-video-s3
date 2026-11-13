# Structure du projet

Avant de commencer, voici l'organisation des dossiers du dépôt GitHub [`imac-s3-video/`](.) :

```text
imac-s3-video/
├── 📁 Rush/                  # Rushs vidéo (Google Drive)
├── 📁 Assets/
│   ├── 📁 Stills/            # Images fixes (Google Drive)
│   ├── 📁 Fonts/             # Polices
│   ├── 📁 LUTs/              # LUTs de colorimétrie
│   ├── 📁 Music/             # Musiques
│   └── 📁 SFX/               # Effets sonores
├── 📁 Grade/                 # Fichiers de color grading
├── 📁 Mix/                   # Exports audio, stems et bounces
├── 📁 Misc/                  # Fichiers divers
└── 📁 Project/
    ├── 📁 DRP/               # Versions du projet DaVinci Resolve
    └── 📁 INCOMING/          # Dépôt temporaire des nouveaux fichiers .drp
```

**# Lors de la première fois**

1. Télécharger les Rush depuis [Google Drive](https://drive.google.com/drive/folders/1E_Tsh7CDggLtbUBF0nYP68kJLn8iDB12?usp=drive_link).
2. Les mettre dans [`Rush/`](Rush/).
3. Télécharger les Stills depuis Google Drive (dans [Assets](https://drive.google.com/drive/folders/1Pn-GwUeY5hkUyO9YnrdLaRxhRo_EiZW2?usp=drive_link)).
4. Les mettre dans [`Assets/Stills/`](Assets/Stills/).
5. Installer les polices présentes dans [`Assets/Fonts/`](Assets/Fonts/) sur son ordinateur.
6. Vérifier que DaVinci Resolve est bien en version 21.2.
7. Récupérer les fichiers présents dans [`Assets/LUTs/`](Assets/LUTs/) et les copier dans le dossier LUT utilisé par DaVinci Resolve :
    - Dans DaVinci : `Project Settings > Color Management > Lookup Tables > Open LUT Folder`.
    - Copier les fichiers dans ce dossier.
    - Retourner dans DaVinci et cliquer sur `Update Lists`.
8. Récupérer les fichiers présents dans [`Grade/`](Grade/) et les importer dans DaVinci si nécessaire.

**# Quand j'ouvre DaVinci**

1. Récupérer la dernière version du dépôt GitHub (`git pull`).
2. Vérifier que personne d'autre ne travaille actuellement sur le projet.
3. Importer la dernière version du projet (dans [`Project/DRP/`](Project/DRP/)).
4. Ouvrir le projet importé.
5. Dans la fenêtre `Media`, cliquer sur l'icône de chaîne rouge et sélectionner le dépôt Git ([`imac-s3-video/`](.)).

**# Lors de mon travail**

1. Ranger les timelines dans le chutier (= un dossier dans la fenêtre `Media`) prévu à cet effet (`Master/Timelines`).
2. Si des LUTs ou fichiers de Grade sont nécessaires, vérifier qu'ils sont bien installés/importés dans DaVinci.

**# Quand j'ai fini**

1. Faire `File > Export Project`.
2. Enregistrer le fichier dans [`Project/INCOMING/`](Project/INCOMING/) et le nommer comme je veux.

    > Le fichier sera automatiquement renommé et déplacé dans [`Project/DRP/`](Project/DRP/) après le commit et le push.

3. Ouvrir un terminal, se placer dans `imac-s3-video/` et exécuter :

    ```bash
    git add .
    git commit -m "CE_QUE_J'AI_FAIT"
    git push
    ```

4. Attendre que la GitHub Action ait terminé, puis faire `git pull` pour récupérer le fichier `.drp` renommé.

**# Exports vidéo**

1. Les exports vidéo doivent être enregistrés dans le dossier [`Export/`](https://drive.google.com/drive/folders/1njuZEBDRhfxJs2WCZeiwxKQXddGoltWw?usp=drive_link) partagé sur Google Drive.
2. Prévenir le groupe lorsqu'un nouvel export est disponible.

**# Avertissements**

> ⚠️ SUIVRE LA STRUCTURE ÉNONCÉE AU DÉBUT.

> ⚠️ NE RIEN CHANGER dans [`Rush/`](Rush/) ou [`Assets/Stills/`](Assets/Stills/) (si possible). En cas de modification, prévenir le groupe et mettre les fichiers à jour sur Google Drive.

> ⚠️ Ne pas déplacer ni supprimer les fichiers originaux dans GitHub ([`Assets/LUTs/`](Assets/LUTs/), [`Grade/`](Grade/), etc.). Toujours conserver les fichiers à leur emplacement d'origine dans le dépôt.

> ⚠️ Les LUTs copiées dans le dossier de DaVinci Resolve doivent rester synchronisées avec celles du dépôt GitHub.

> ⚠️ Le dossier [`Export/`](https://drive.google.com/drive/folders/1njuZEBDRhfxJs2WCZeiwxKQXddGoltWw?usp=drive_link) est stocké sur Google Drive.
