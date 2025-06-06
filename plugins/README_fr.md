# Modules de scraping

Chaque implémentation de scraper se trouve dans son propre fichier de ce dossier. Un plugin doit définir une sous-classe de `BaseScraper` et implémenter les méthodes utilisées par l'application (`scrape_product`, `scrape_images`, `scrap_produits_par_ids`, etc.).

Pour ajouter un nouveau connecteur :
1. Créez un fichier `votreplateforme.py` ici.
2. Définissez `class YourScraper(BaseScraper)` avec les méthodes requises.
3. Modifiez `config.toml` pour `SCRAPER_PLUGIN = "plugins.votreplateforme"`.

`ScraperCore` chargera automatiquement le plugin indiqué dans cette valeur de configuration.
