# Installation et utilisation

## Prérequis
- Python 3.10 ou supérieur
- Google Chrome (le pilote est téléchargé automatiquement si `CHROME_DRIVER_PATH` est vide)

Installez le projet avec :
```bash
pip install .
```

Pour utiliser le scraping asynchrone, installez également les navigateurs `playwright` :
```bash
playwright install
```

### Démarrage rapide
```bash
pip install .
python Application.py
```

### Autres modes d'installation
- **Docker**
  ```bash
  docker build -t woocommerce-scraper .
  docker run --rm woocommerce-scraper
  ```
- **Exécutable autonome**
  ```bash
  ./build.sh
  dist/woocommerce-scraper --help
  ```

### Lancer les tests
```bash
pip install .[test]
pytest
```

### Paramétrage
Les chemins sont stockés dans `config.toml` à la racine du dépôt. S'il est absent, un fichier par défaut est créé.

### Utilisation de l'application
Lancez l'interface PySide6 avec :
```bash
python Application.py
```
Elle permet d'effectuer le scraping, l'optimisation des images et de consulter les rapports.

### D\u00e9marrage du serveur Flask
`Application.py` (ou `app.py` selon la version) lance automatiquement
`flask_server.py` en arri\u00e8re-plan sur le port `5000`. Le serveur se termine
quand l'interface se ferme.

Pour d\u00e9marrer le serveur manuellement :

```bash
python flask_server.py
```

Arr\u00eatez-le avec `Ctrl+C` ou en fermant le processus.

### Surveillance des logs
Tous les messages sont enregistr\u00e9s dans `logs/app.log`. Utilisez :

```bash
tail -f logs/app.log
```

pour suivre l'activit\u00e9 en temps r\u00e9el.

## Microservices Node.js / Go
Les microservices suppl\u00e9mentaires se trouvent dans `js_modules` et
`go_modules`.

Pour lancer un service Node.js :

```bash
cd js_modules/mon_service
npm install
npm start    # ou node dist/index.js
```

Pour un service Go :

```bash
cd go_modules/mon_service
go build
./mon_service
```

Interrompez-les avec `Ctrl+C` et interagissez via leur API HTTP avec `curl` ou
l'application principale.
## Modules natifs (C/Rust)

Des exemples simples se trouvent dans les dossiers `c_modules` et `rust_modules`. Celui de `c_modules/hello` expose une fonction `add`. Compilez-le avec :

```bash
cd c_modules/hello
make
```

Le fichier `libhello.so` peut être chargé depuis Python grâce à `ctypes` :

```python
from ctypes import CDLL, c_int
lib = CDLL("c_modules/hello/libhello.so")
print(lib.add(c_int(2), c_int(3)))  # 5
```

Le projet `rust_modules/hello` fournit une fonction `multiply`. Compilez-le :

```bash
cd rust_modules/hello
cargo build --release
```

Le fichier compilé `target/release/libhello.so` se charge de la même manière :

```python
from ctypes import CDLL
lib = CDLL("rust_modules/hello/target/release/libhello.so")
print(lib.multiply(4, 5))  # 20
```

