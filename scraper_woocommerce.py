import os
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata
import time
import random
import requests
import urllib.request
from urllib.parse import urlparse
import config

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# === CORE CLASS ===

class ScraperCore:
    """Centralise configuration and scraping helpers."""

    def __init__(self, base_dir=config.BASE_DIR,
                 chrome_driver_path=config.CHROME_DRIVER_PATH,
                 chrome_binary_path=config.CHROME_BINARY_PATH):
        self.base_dir = base_dir
        self.chrome_driver_path = chrome_driver_path
        self.chrome_binary_path = chrome_binary_path

        self.fiche_dir = os.path.join(self.base_dir, "optimisation_fiches")
        self.liens_id_txt = os.path.join(self.base_dir, "liens_avec_id.txt")
        self.chemin_liens_images = os.path.join(self.base_dir, "liens_images_details.xlsx")

        self.fichier_excel = os.path.join(self.base_dir, "woocommerce_mix.xlsx")
        self.save_directory = os.path.join(self.base_dir, "fiche concurrents")
        self.recap_excel_path = os.path.join(self.base_dir, "recap_concurrents.xlsx")

        self.results_dir = ""
        self.json_dir = ""

        self._progress = 0
        self._logs = []

    # --- Utility helpers -------------------------------------------------
    @staticmethod
    def clean_name(name):
        nfkd = unicodedata.normalize('NFKD', name)
        only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
        return only_ascii.lower().replace('-', ' ').strip()

    @staticmethod
    def clean_filename(name):
        nfkd = unicodedata.normalize('NFKD', name)
        only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
        safe = re.sub(r"[^a-zA-Z0-9\- ]", "", only_ascii)
        safe = safe.replace(" ", "-").lower()
        return safe

    def charger_liens_avec_id(self, path=None):
        path = path or self.liens_id_txt
        id_url_map = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '|' in line:
                    identifiant, url = line.split('|', 1)
                else:
                    parts = line.split(" ", 1)
                    if len(parts) != 2:
                        continue
                    identifiant, url = parts
                id_url_map[identifiant.strip().upper()] = url.strip()
        return id_url_map

    def charger_liste_ids(self, path=None):
        path = path or self.liens_id_txt
        ids = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '|' in line:
                    part = line.split('|', 1)[0]
                else:
                    part = line.split(" ", 1)[0]
                if part:
                    ids.append(part.upper())
        ids.sort(key=lambda x: int(re.search(r"\d+", x).group()))
        return ids

    def charger_liste_urls(self, path=None):
        path = path or self.liens_id_txt
        urls = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '|' in line:
                    part = line.split('|', 1)[1]
                else:
                    parts = line.split(' ', 1)
                    part = parts[1] if len(parts) == 2 else ''
                if part:
                    urls.append(part.strip())
        return urls

    # --- Runtime configuration ------------------------------------------
    def prepare_results_dir(self, selected_base, result_name):
        base_path = os.path.join(selected_base, result_name)
        final_path = base_path
        if os.path.exists(final_path):
            idx = 2
            while os.path.exists(f"{base_path}_{idx}"):
                idx += 1
            final_path = f"{base_path}_{idx}"

        self.results_dir = final_path
        descriptions_dir = os.path.join(self.results_dir, "descriptions")
        self.json_dir = os.path.join(self.results_dir, "json")
        xlsx_dir = os.path.join(self.results_dir, "xlsx")
        os.makedirs(descriptions_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(xlsx_dir, exist_ok=True)
        self.save_directory = descriptions_dir
        self.fichier_excel = os.path.join(xlsx_dir, "woocommerce_mix.xlsx")
        self.recap_excel_path = os.path.join(xlsx_dir, "recap_concurrents.xlsx")

    # --- Progress / logging helpers ------------------------------------
    def _update_progress(self, value):
        self._progress = int(value)

    def _log(self, message):
        self._logs.append(str(message))
        print(message)

    def get_progress(self):
        return self._progress

    def get_logs(self):
        return "\n".join(self._logs)

    # --- High level orchestration -------------------------------------
    def start_scraping(
        self,
        id_url_map,
        ids_selectionnes,
        sections,
        driver_path=None,
        binary_path=None,
        batch_size=50,
        progress_callback=None,
        headless=True,
    ):
        """Run selected scraping sections with progress aggregation."""
        progress_callback = progress_callback or self._update_progress
        total = len(sections)
        done = 0
        summary = []

        def scaled(p):
            overall = int(done / total * 100 + p / total)
            progress_callback(overall)

        if 'variantes' in sections:
            ok, err = self.scrap_produits_par_ids(
                id_url_map,
                ids_selectionnes,
                driver_path,
                binary_path,
                progress_callback=scaled,
                headless=headless,
            )
            summary.append(f"Variantes: {ok} OK, {err} erreurs")
            done += 1

        if 'concurrents' in sections:
            ok, err = self.scrap_fiches_concurrents(
                id_url_map,
                ids_selectionnes,
                driver_path,
                binary_path,
                progress_callback=scaled,
                headless=headless,
            )
            summary.append(f"Concurrents: {ok} OK, {err} erreurs")
            done += 1

        if 'json' in sections:
            self.export_fiches_concurrents_json(batch_size, progress_callback=scaled)
            summary.append("Export JSON termin\u00e9")
            done += 1

        progress_callback(100)
        return "\n".join(summary)

# === SCRAPING PRODUITS (VARIANTES) ===
    def scrap_produits_par_ids(self, id_url_map, ids_selectionnes, driver_path=None, binary_path=None, progress_callback=None, should_stop=lambda: False, headless=True):
        driver_path = driver_path or self.chrome_driver_path
        binary_path = binary_path or self.chrome_binary_path
        if not driver_path:
            try:
                driver_path = ChromeDriverManager().install()
            except Exception as e:
                self._log(f"❌ Impossible de télécharger ChromeDriver : {e}")
                self._log("➡️ Spécifiez CHROME_DRIVER_PATH pour un mode hors-ligne.")
                return 0, len(ids_selectionnes)
        progress_callback = progress_callback or self._update_progress
        options = webdriver.ChromeOptions()
        if binary_path:
            options.binary_location = binary_path
        if headless:
            options.add_argument("--headless")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        woocommerce_rows = []
        n_ok = 0
        n_err = 0

        total = len(ids_selectionnes)
        self._log(f"\n🚀 Début du scraping de {total} liens...\n")
        for idx, id_produit in enumerate(ids_selectionnes, start=1):
            if should_stop():
                self._log("⏹ Interruption demandée.")
                progress_callback(100)
                break
            url = id_url_map.get(id_produit)
            if not url:
                self._log(f"❌ ID introuvable dans le fichier : {id_produit}")
                n_err += 1
                continue

            self._log(f"🔎 [{idx}/{len(ids_selectionnes)}] {id_produit} → {url}")
            try:
                driver.get(url)
                time.sleep(random.uniform(2.5, 3.5))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
                time.sleep(2)

                product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
                base_sku = re.sub(r'\W+', '-', product_name.lower()).strip("-")[:15].upper()
                product_price = ""

                for selector in ["sale-price.text-lg", ".price", ".product-price", ".woocommerce-Price-amount"]:
                    try:
                        elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if elem and elem.text.strip():
                            match = re.search(r"([0-9]+(?:[\\.,][0-9]{2})?)", elem.text.strip())
                            if match:
                                product_price = match.group(1).replace(",", ".")
                            break
                    except Exception:
                        continue

                variant_labels = driver.find_elements(By.CSS_SELECTOR, "label.color-swatch")
                visible_labels = [label for label in variant_labels if label.is_displayed()]
                variant_names = []

                for label in visible_labels:
                    try:
                        name = label.find_element(By.CSS_SELECTOR, "span.sr-only").text.strip()
                        variant_names.append(name)
                    except Exception:
                        continue

                nom_dossier = self.clean_name(product_name).replace(" ", "-")

                if len(variant_names) <= 1:
                    woocommerce_rows.append({
                        "ID Produit": id_produit,
                        "Type": "simple",
                        "SKU": base_sku,
                        "Name": product_name,
                        "Regular price": product_price,
                        "Nom du dossier": nom_dossier
                    })
                    continue

                woocommerce_rows.append({
                    "ID Produit": id_produit,
                    "Type": "variable",
                    "SKU": base_sku,
                    "Name": product_name,
                    "Parent": "",
                    "Attribute 1 name": "Couleur",
                    "Attribute 1 value(s)": " | ".join(variant_names),
                    "Attribute 1 default": variant_names[0],
                    "Regular price": "",
                    "Nom du dossier": nom_dossier
                })

                for v in variant_names:
                    clean_v = re.sub(r'\W+', '', v).upper()
                    child_sku = f"{base_sku}-{clean_v}"
                    woocommerce_rows.append({
                        "ID Produit": id_produit,
                        "Type": "variation",
                        "SKU": child_sku,
                        "Name": "",
                        "Parent": base_sku,
                        "Attribute 1 name": "Couleur",
                        "Attribute 1 value(s)": v,
                        "Regular price": product_price,
                        "Nom du dossier": nom_dossier
                    })

            except Exception as e:
                self._log(f"❌ Erreur sur {url} → {e}\n")
                n_err += 1
                continue
            else:
                n_ok += 1

            if progress_callback:
                progress_callback(int(idx / total * 100))

        driver.quit()
        df = pd.DataFrame(woocommerce_rows)
        df.to_excel(self.fichier_excel, index=False)
        self._log(f"\n📁 Données sauvegardées dans : {self.fichier_excel}")
        return n_ok, n_err

# === SCRAPING FICHES CONCURRENTS ===
    def scrap_fiches_concurrents(self, id_url_map, ids_selectionnes, driver_path=None, binary_path=None, progress_callback=None, should_stop=lambda: False, headless=True):
        driver_path = driver_path or self.chrome_driver_path
        binary_path = binary_path or self.chrome_binary_path
        if not driver_path:
            try:
                driver_path = ChromeDriverManager().install()
            except Exception as e:
                self._log(f"❌ Impossible de télécharger ChromeDriver : {e}")
                self._log("➡️ Spécifiez CHROME_DRIVER_PATH pour un mode hors-ligne.")
                return 0, len(ids_selectionnes)
        progress_callback = progress_callback or self._update_progress
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        if binary_path:
            options.binary_location = binary_path
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        if headless:
            options.add_argument("--headless")

        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        os.makedirs(self.save_directory, exist_ok=True)
        recap_data = []
        n_ok = 0
        n_err = 0
        total = len(ids_selectionnes)
        for idx, id_produit in enumerate(ids_selectionnes, start=1):
            if should_stop():
                self._log("⏹ Interruption demandée.")
                progress_callback(100)
                break
            url = id_url_map.get(id_produit)
            if not url:
                self._log(f"\n❌ ID introuvable dans le fichier : {id_produit}")
                recap_data.append(("?", "?", id_produit, "ID non trouvé"))
                n_err += 1
                continue

            self._log(f"\n📦 {idx} / {total}")
            self._log(f"🔗 {url} — ")

            try:
                driver.get(url)
                time.sleep(random.uniform(2.5, 4.2))  # anti-bot

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                title_tag = (
                    soup.find("h1", class_="product-single__title") or
                    soup.find("h1", class_="product-info__title") or
                    soup.find("h1")
                )
                if not title_tag:
                    raise Exception("❌ Titre produit introuvable")
                title = title_tag.get_text(strip=True)
                filename = self.clean_filename(title) + ".txt"
                txt_path = os.path.join(self.save_directory, filename)

                description_div = None
                description_div = soup.find("div", {"id": "product_description"})
                if not description_div:
                    container = soup.find("div", class_="accordion__content")
                    if container:
                        description_div = container.find("div", class_="prose")
                if not description_div:
                    description_div = soup.find("div", class_="prose")
                if not description_div:
                    raise Exception("❌ Description introuvable")

                def convert_links(tag):
                    for a in tag.find_all("a", href=True):
                        text = a.get_text(strip=True)
                        href = a['href']
                        markdown = f"[{text}]({href})"
                        a.replace_with(markdown)

                convert_links(description_div)
                raw_html = str(description_div)

                txt_content = f"<h1>{title}</h1>\n\n{raw_html}"
                with open(txt_path, "w", encoding="utf-8") as f2:
                    f2.write(txt_content)

                self._log(f"✅ Extraction OK ({filename})")
                recap_data.append((filename, title, url, "Extraction OK"))
                n_ok += 1
            except Exception as e:
                self._log(f"❌ Extraction Échec — {str(e)}")
                recap_data.append(("?", "?", url, "Extraction Échec"))
                n_err += 1

            if progress_callback:
                progress_callback(int(idx / total * 100))

        df = pd.DataFrame(recap_data, columns=["Nom du fichier", "H1", "Lien", "Statut"])
        df.to_excel(self.recap_excel_path, index=False)
        driver.quit()
        self._log("\n🎉 Extraction terminée. Résultats enregistrés dans :")
        self._log(f"- 📁 Fiches : {self.save_directory}")
        self._log(f"- 📊 Récapitulatif : {self.recap_excel_path}")
        return n_ok, n_err

# === EXPORT JSON PAR BATCH ===
    def export_fiches_concurrents_json(self, taille_batch=50, progress_callback=None, should_stop=lambda: False):
        progress_callback = progress_callback or self._update_progress
        dossier_source = self.save_directory
        dossier_sortie = self.json_dir if self.json_dir else os.path.join(dossier_source, "batches_json")
        os.makedirs(dossier_sortie, exist_ok=True)
        fichiers_txt = [f for f in os.listdir(dossier_source) if f.endswith(".txt")]
        fichiers_txt.sort()
        total = len(fichiers_txt)
        id_global = 1

        def extraire_h1(html):
            match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else ""

        processed = 0
        nb_fichiers = 0
        for i in range(0, len(fichiers_txt), taille_batch):
            if should_stop():
                self._log("⏹ Interruption demandée.")
                progress_callback(100)
                break
            batch = fichiers_txt[i:i+taille_batch]
            data_batch = []

            nb_fichiers += 1
            self._log(f"\n🔹 Batch {nb_fichiers} : {len(batch)} fichier(s)")
            for fichier in batch:
                if should_stop():
                    progress_callback(100)
                    break
                chemin = os.path.join(dossier_source, fichier)
                try:
                    with open(chemin, "r", encoding="utf-8") as f:
                        contenu = f.read()
                    h1 = extraire_h1(contenu)
                    id_source = os.path.splitext(fichier)[0]
                    data_batch.append({
                        "id": id_global,
                        "id_source": id_source,
                        "nom": fichier,
                        "h1": h1,
                        "html": contenu.strip()
                    })
                    self._log(f"  ✅ {fichier} — h1: {h1[:50]}...")
                except Exception as e:
                    self._log(f"  ⚠️ Erreur lecture {fichier}: {e}")
                    continue
                id_global += 1
                processed += 1
                if progress_callback:
                    progress_callback(int(processed / total * 100))

            nom_fichier_sortie = f"batch_{i//taille_batch + 1}.json"
            chemin_sortie = os.path.join(dossier_sortie, nom_fichier_sortie)
            with open(chemin_sortie, "w", encoding="utf-8") as f_json:
                json.dump(data_batch, f_json, ensure_ascii=False, indent=2)

            self._log(f"    ➡️ Batch sauvegardé : {nom_fichier_sortie} ({len(batch)} produits)")

        self._log(f"\n✅ Export JSON terminé : {nb_fichiers} fichier(s) généré(s) dans : {dossier_sortie}")

    # === SCRAPING IMAGES ===
    def scrap_images(
        self,
        urls,
        dest_folder,
        driver_path=None,
        binary_path=None,
        suffix="image-produit",
        progress_callback=None,
        preview_callback=None,
        should_stop=lambda: False,
        headless=True,
    ):
        driver_path = driver_path or self.chrome_driver_path
        binary_path = binary_path or self.chrome_binary_path
        if not driver_path:
            try:
                driver_path = ChromeDriverManager().install()
            except Exception as e:
                self._log(f"❌ Impossible de télécharger ChromeDriver : {e}")
                self._log("➡️ Spécifiez CHROME_DRIVER_PATH pour un mode hors-ligne.")
                return "Erreur téléchargement ChromeDriver"
        progress_callback = progress_callback or self._update_progress

        options = webdriver.ChromeOptions()
        if binary_path:
            options.binary_location = binary_path
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        if headless:
            options.add_argument("--headless")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )

        os.makedirs(dest_folder, exist_ok=True)
        failed = []
        total = len(urls)
        for idx, url in enumerate(urls, start=1):
            if should_stop():
                self._log("⏹ Interruption demandée.")
                progress_callback(100)
                break
            self._log(f"\n🔍 Produit {idx}/{total} : {url}")
            if idx > 1 and idx % 25 == 0:
                self._log("🔄 Redémarrage du navigateur pour libérer la mémoire...")
                driver.quit()
                time.sleep(3)
                driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=options)
                driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
                )

            try:
                driver.get(url)
                time.sleep(random.uniform(2.5, 4.5))

                raw_title = driver.title.strip().split("|")[0].strip()
                folder_name = self.clean_filename(raw_title)
                folder = os.path.join(dest_folder, folder_name)
                os.makedirs(folder, exist_ok=True)

                images = driver.find_elements(By.CSS_SELECTOR, ".product-gallery__media img")
                self._log(f"🖼️ {len(images)} image(s) trouvée(s)")

                for i, img in enumerate(images):
                    if should_stop():
                        progress_callback(100)
                        break
                    src = img.get_attribute("src")
                    if not src:
                        continue
                    try:
                        temp_path = os.path.join(folder, f"temp_{i}.webp")
                        urllib.request.urlretrieve(src, temp_path)

                        name = os.path.splitext(os.path.basename(urlparse(src).path))[0]
                        name = re.sub(r"-\d{3,4}", "", name)
                        name = re.sub(r"[-]+", "-", name).strip("-")
                        alt_text = f"{name.replace('-', ' ')} – {suffix}"
                        filename = self.clean_filename(alt_text) + ".webp"
                        final_path = os.path.join(folder, filename)
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        os.rename(temp_path, final_path)

                        self._log(f"   ✅ Image {i+1} → {filename}")
                        self._log(f"      ↪️ Texte ALT : {alt_text}")
                        if preview_callback:
                            preview_callback(final_path)
                        time.sleep(random.uniform(1, 2))
                    except Exception as img_err:
                        self._log(f"   ❌ Échec de téléchargement pour image {i+1} : {img_err}")
                        failed.append((url, src))

                self._log(f"📁 Téléchargement terminé pour : {folder_name}")
            except Exception as e:
                self._log(f"❌ Erreur sur la page {url} : {e}")

            if progress_callback:
                progress_callback(int(idx / total * 100))
            self._log("-" * 80)
            time.sleep(random.uniform(1.5, 3))

        driver.quit()

        if failed:
            self._log("\n❗Images échouées :")
            for u, src in failed:
                self._log(f"Produit : {u} → Image : {src}")
            self._log(f"Total échouées : {len(failed)}")
        else:
            self._log("\n✅ Toutes les images ont été téléchargées avec succès.")

        if progress_callback:
            progress_callback(100)
        return "Scraping images terminé"

    # === SERVER INTERACTION ===
    def run_flask_server(self, fiche_folder, batch_size=15):
        import flask_server
        self._log(f"Lancement du serveur Flask sur le dossier {fiche_folder}")
        flask_server.DOSSIER_FICHES = fiche_folder
        flask_server.PRODUITS_PAR_BATCH = batch_size
        flask_server.app.run(port=5000)

    def upload_fiche(self, fiche_path, fiche_id=None):
        if not os.path.exists(fiche_path):
            self._log(f"Fichier introuvable: {fiche_path}")
            return
        with open(fiche_path, "r", encoding="utf-8") as f:
            html = f.read()
        name = os.path.basename(fiche_path)
        fiche_id = fiche_id or os.path.splitext(name)[0]
        payload = {"id": fiche_id, "nom": name, "html": html}
        try:
            r = requests.post("http://127.0.0.1:5000/upload-fiche", json=payload)
            self._log(str(r.json()))
        except Exception as e:
            self._log(f"Erreur upload: {e}")

    def list_fiches(self):
        try:
            r = requests.get("http://127.0.0.1:5000/list-fiches")
            self._log(str(r.json()))
        except Exception as e:
            self._log(f"Erreur list fiches: {e}")


