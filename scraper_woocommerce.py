import os
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata
import time
import random
import requests
import config

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

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

    def charger_liens_avec_id(self):
        id_url_map = {}
        with open(self.liens_id_txt, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    identifiant, url = parts
                    id_url_map[identifiant.upper()] = url
        return id_url_map

    def charger_liste_ids(self):
        ids = []
        with open(self.liens_id_txt, "r", encoding="utf-8") as f:
            for line in f:
                part = line.strip().split(" ", 1)[0]
                if part:
                    ids.append(part.upper())
        ids.sort(key=lambda x: int(re.search(r"\d+", x).group()))
        return ids

    # --- Runtime configuration ------------------------------------------
    def prepare_results_dir(self, selected_base, result_name):
        self.results_dir = os.path.join(selected_base, result_name)
        descriptions_dir = os.path.join(self.results_dir, "descriptions")
        self.json_dir = os.path.join(self.results_dir, "json")
        xlsx_dir = os.path.join(self.results_dir, "xlsx")
        os.makedirs(descriptions_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(xlsx_dir, exist_ok=True)
        self.save_directory = descriptions_dir
        self.fichier_excel = os.path.join(xlsx_dir, "woocommerce_mix.xlsx")
        self.recap_excel_path = os.path.join(xlsx_dir, "recap_concurrents.xlsx")

# === SCRAPING PRODUITS (VARIANTES) ===
    def scrap_produits_par_ids(self, id_url_map, ids_selectionnes, driver_path=None, binary_path=None):
        driver_path = driver_path or self.chrome_driver_path
        binary_path = binary_path or self.chrome_binary_path
        options = webdriver.ChromeOptions()
        options.binary_location = binary_path
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

        print(f"\n🚀 Début du scraping de {len(ids_selectionnes)} liens...\n")
        for idx, id_produit in enumerate(ids_selectionnes, start=1):
            url = id_url_map.get(id_produit)
            if not url:
                print(f"❌ ID introuvable dans le fichier : {id_produit}")
                n_err += 1
                continue

            print(f"🔎 [{idx}/{len(ids_selectionnes)}] {id_produit} → {url}")
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
                print(f"❌ Erreur sur {url} → {e}\n")
                n_err += 1
                continue
            else:
                n_ok += 1

        driver.quit()
        df = pd.DataFrame(woocommerce_rows)
        df.to_excel(self.fichier_excel, index=False)
        print(f"\n📁 Données sauvegardées dans : {self.fichier_excel}")
        return n_ok, n_err

# === SCRAPING FICHES CONCURRENTS ===
    def scrap_fiches_concurrents(self, id_url_map, ids_selectionnes, driver_path=None, binary_path=None):
        driver_path = driver_path or self.chrome_driver_path
        binary_path = binary_path or self.chrome_binary_path
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        options.binary_location = binary_path
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

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
            url = id_url_map.get(id_produit)
            if not url:
                print(f"\n❌ ID introuvable dans le fichier : {id_produit}")
                recap_data.append(("?", "?", id_produit, "ID non trouvé"))
                n_err += 1
                continue

            print(f"\n📦 {idx} / {total}")
            print(f"🔗 {url} — ", end="")

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

                print(f"✅ Extraction OK ({filename})")
                recap_data.append((filename, title, url, "Extraction OK"))
                n_ok += 1
            except Exception as e:
                print(f"❌ Extraction Échec — {str(e)}")
                recap_data.append(("?", "?", url, "Extraction Échec"))
                n_err += 1

        df = pd.DataFrame(recap_data, columns=["Nom du fichier", "H1", "Lien", "Statut"])
        df.to_excel(self.recap_excel_path, index=False)
        driver.quit()
        print("\n🎉 Extraction terminée. Résultats enregistrés dans :")
        print(f"- 📁 Fiches : {self.save_directory}")
        print(f"- 📊 Récapitulatif : {self.recap_excel_path}")
        return n_ok, n_err

# === EXPORT JSON PAR BATCH ===
    def export_fiches_concurrents_json(self, taille_batch=5):
        dossier_source = self.save_directory
        dossier_sortie = self.json_dir if self.json_dir else os.path.join(dossier_source, "batches_json")
        os.makedirs(dossier_sortie, exist_ok=True)
        fichiers_txt = [f for f in os.listdir(dossier_source) if f.endswith(".txt")]
        fichiers_txt.sort()
        id_global = 1

        def extraire_h1(html):
            match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else ""

        for i in range(0, len(fichiers_txt), taille_batch):
            batch = fichiers_txt[i:i+taille_batch]
            data_batch = []

            print(f"\n🔹 Batch {i//taille_batch + 1} : {len(batch)} fichiers")
            for fichier in batch:
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
                    print(f"  ✅ {fichier} — h1: {h1[:50]}...")
                except Exception as e:
                    print(f"  ⚠️ Erreur lecture {fichier}: {e}")
                    continue
                id_global += 1

            nom_fichier_sortie = f"batch_{i//taille_batch + 1}.json"
            chemin_sortie = os.path.join(dossier_sortie, nom_fichier_sortie)
            with open(chemin_sortie, "w", encoding="utf-8") as f_json:
                json.dump(data_batch, f_json, ensure_ascii=False, indent=2)

            print(f"    ➡️ Batch sauvegardé : {nom_fichier_sortie}")

        print("\n✅ Export JSON terminé avec lots de 5 produits. Fichiers créés dans :", dossier_sortie)

    # === SERVER INTERACTION ===
    def run_flask_server(self, fiche_folder, batch_size=15):
        import flask_server
        flask_server.DOSSIER_FICHES = fiche_folder
        flask_server.PRODUITS_PAR_BATCH = batch_size
        flask_server.app.run(port=5000)

    def upload_fiche(self, fiche_path, fiche_id=None):
        if not os.path.exists(fiche_path):
            print(f"Fichier introuvable: {fiche_path}")
            return
        with open(fiche_path, "r", encoding="utf-8") as f:
            html = f.read()
        name = os.path.basename(fiche_path)
        fiche_id = fiche_id or os.path.splitext(name)[0]
        payload = {"id": fiche_id, "nom": name, "html": html}
        try:
            r = requests.post("http://127.0.0.1:5000/upload-fiche", json=payload)
            print(r.json())
        except Exception as e:
            print("Erreur upload:", e)

    def list_fiches(self):
        try:
            r = requests.get("http://127.0.0.1:5000/list-fiches")
            print(r.json())
        except Exception as e:
            print("Erreur list fiches:", e)


