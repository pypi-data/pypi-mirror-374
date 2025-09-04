### How 2 install ?

-   Avoir un mac
-   Ouvrir un terminal
-   Installer <a href="https://docs.astral.sh/uv/" class="external-link" target="_blank">uv</a>:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

-   Vérifier l'installation de uv:

```bash
uv --version
```

-   Installer <a href="https://gitlab.com/unico-dev/device-setuper" class="external-link" target="_blank">device-setuper</a>:

```bash
uv tool install unico_device_setuper
```

-   Vérifier l'installation device-setuper:

```bash
device-setup --version
```

---

### How 2 mettre à jour ?

```bash
uv tool upgrade unico_device_setuper
```

---

### Utilisation

-   Ouvrir un terminal

```bash
device-setup
```

-   Se laisser guider 🧑‍🦯‍➡️

---

### Faire tourner en local

-   Suivre les étapes <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" class="external-link" target="_blank">plus haut</a> pour installer uv

-   Clone le répo:

```bash
git clone git@gitlab.com:unico-dev/device-setuper.git && cd device-setuper
```

-   Installer les dépendances:

```bash
uv sync
```

-   Rentrer dans l'environement virtuel

```bash
source .venv/bin/activate
```

-   Créer puis (probablement me demander pour) remplir le fichier d'environement:

```bash
touch config.toml
```

-   Pour lancer le backend:

```bash
device-setuper-backend
```

-   Pour lancer la cli:

```bash
device-setup
```
