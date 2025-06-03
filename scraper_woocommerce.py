import os
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata
import time, random
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# === CONFIGURATION ===
base_dir = r"C:\Users\Lamine\Desktop\woocommerce\code\CODE POUR BOB"
chrome_driver_path = os.path.join(base_dir, r"../chromdrivers 137/chromedriver-win64/chromedriver.exe")
chrome_binary_path = os.path.join(base_dir, r"../chromdrivers 137/chrome-win64/chrome.exe")

fiche_dir = os.path.join(base_dir, "optimisation_fiches")
liens_id_txt = os.path.join(base_dir, "liens_avec_id.txt")
chemin_liens_images = os.path.join(base_dir, "liens_images_details.xlsx")

# Paths related to results will be defined at runtime from the UI
# base_dir can be overridden from the Tkinter interface
fichier_excel = os.path.join(base_dir, "woocommerce_mix.xlsx")
save_directory = os.path.join(base_dir, "fiche concurrents")
recap_excel_path = os.path.join(base_dir, "recap_concurrents.xlsx")
results_dir = ""
json_dir = ""

# === UTILS ===
def clean_name(name):
    nfkd = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower().replace('-', ' ').strip()

def clean_filename(name):
    nfkd = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    safe = re.sub(r"[^a-zA-Z0-9\- ]", "", only_ascii)
    safe = safe.replace(" ", "-").lower()
    return safe

def charger_liens_avec_id():
    id_url_map = {}
    with open(liens_id_txt, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                identifiant, url = parts
                id_url_map[identifiant.upper()] = url
    return id_url_map

def charger_liste_ids():
    ids = []
    with open(liens_id_txt, "r", encoding="utf-8") as f:
        for line in f:
            part = line.strip().split(" ", 1)[0]
            if part:
                ids.append(part.upper())
    ids.sort(key=lambda x: int(re.search(r"\d+", x).group()))
    return ids

# === SCRAPING PRODUITS (VARIANTES) ===
def scrap_produits_par_ids(id_url_map, ids_selectionnes):
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    options.add_argument("--headless")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(executable_path=chrome_driver_path)
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
                except:
                    continue

            variant_labels = driver.find_elements(By.CSS_SELECTOR, "label.color-swatch")
            visible_labels = [label for label in variant_labels if label.is_displayed()]
            variant_names = []

            for label in visible_labels:
                try:
                    name = label.find_element(By.CSS_SELECTOR, "span.sr-only").text.strip()
                    variant_names.append(name)
                except:
                    continue

            nom_dossier = clean_name(product_name).replace(" ", "-")

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
    df.to_excel(fichier_excel, index=False)
    print(f"\n📁 Données sauvegardées dans : {fichier_excel}")
    return n_ok, n_err

# === SCRAPING FICHES CONCURRENTS ===
def scrap_fiches_concurrents(id_url_map, ids_selectionnes):
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    os.makedirs(save_directory, exist_ok=True)
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
            filename = clean_filename(title) + ".txt"
            txt_path = os.path.join(save_directory, filename)

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
    df.to_excel(recap_excel_path, index=False)
    driver.quit()
    print("\n🎉 Extraction terminée. Résultats enregistrés dans :")
    print(f"- 📁 Fiches : {save_directory}")
    print(f"- 📊 Récapitulatif : {recap_excel_path}")
    return n_ok, n_err

# === EXPORT JSON PAR BATCH ===
def export_fiches_concurrents_json(taille_batch=5):
    dossier_source = save_directory
    dossier_sortie = json_dir if json_dir else os.path.join(dossier_source, "batches_json")
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

# === INTERFACE INTERACTIVE ===
if __name__ == "__main__":
    import sys
    import threading
    import tkinter as tk
    from tkinter import scrolledtext, ttk, filedialog, messagebox

    id_url_map = charger_liens_avec_id()
    id_list = charger_liste_ids()

    class TextRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)
            self.widget.configure(state="disabled")

        def flush(self):
            pass

    def get_ids_from_selection():
        try:
            start = id_list.index(start_var.get())
            end = id_list.index(end_var.get())
            if start > end:
                print("⛔ ID de début supérieur à l'ID de fin.\n")
                return []
            return id_list[start:end+1]
        except ValueError:
            print("⛔ Sélection d'ID invalide.\n")
            return []

    def execute_actions():
        ids = get_ids_from_selection()
        if not ids:
            return

        result_name = entry_result.get().strip() or "Resultats"
        global results_dir, save_directory, recap_excel_path, fichier_excel, json_dir
        selected_base = base_dir_var.get() or base_dir
        results_dir = os.path.join(selected_base, result_name)
        descriptions_dir = os.path.join(results_dir, "descriptions")
        json_dir = os.path.join(results_dir, "json")
        xlsx_dir = os.path.join(results_dir, "xlsx")
        os.makedirs(descriptions_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(xlsx_dir, exist_ok=True)
        save_directory = descriptions_dir
        fichier_excel = os.path.join(xlsx_dir, "woocommerce_mix.xlsx")
        recap_excel_path = os.path.join(xlsx_dir, "recap_concurrents.xlsx")

        actions = []
        if var_variantes.get():
            actions.append(lambda: scrap_produits_par_ids(id_url_map, ids))
        if var_concurrents.get():
            actions.append(lambda: scrap_fiches_concurrents(id_url_map, ids))
        if var_json.get():
            actions.append(export_fiches_concurrents_json)

        if not actions:
            print("⛔ Aucune action sélectionnée.\n")
            return

        def run_all():
            status_var.set("Exécution en cours...")
            n_ok_total = 0
            n_err_total = 0
            for act in actions:
                res = act()
                if isinstance(res, tuple) and len(res) == 2:
                    ok, err = res
                    n_ok_total += ok
                    n_err_total += err
            status_var.set("Exécution terminée")
            summary = (
                f"✅ {n_ok_total} produits scrappés, "
                f"❌ {n_err_total} erreurs, "
                f"📁 Données dans: {results_dir}"
            )
            print(summary)
            try:
                messagebox.showinfo("Récapitulatif", summary)
            except Exception:
                pass

        threading.Thread(target=run_all, daemon=True).start()

    def open_results_folder():
        import subprocess
        import platform
        default_path = os.path.join(base_dir_var.get() or base_dir, "fiche concurrents")
        path = results_dir if results_dir else default_path
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def start_flask_server():
        def run():
            import subprocess, sys
            try:
                subprocess.Popen([sys.executable, "flask_server.py"])
                print("🚀 Serveur Flask démarré")
            except Exception as e:
                print(f"❌ Erreur lancement Flask: {e}")
        threading.Thread(target=run, daemon=True).start()

    def load_batch():
        batch = batch_var.get()
        def run():
            try:
                resp = requests.get("http://localhost:5000/get-produits", params={"batch": batch})
                print(resp.text)
            except Exception as e:
                print(f"❌ Erreur GET /get-produits: {e}")
        threading.Thread(target=run, daemon=True).start()

    def upload_fiches():
        directory = fiches_dir_var.get()
        def run():
            if not os.path.exists(directory):
                print(f"❌ Dossier inexistant: {directory}")
                return
            fichiers = [f for f in os.listdir(directory) if f.endswith(".txt")]
            for idx, fichier in enumerate(fichiers, start=1):
                chemin = os.path.join(directory, fichier)
                try:
                    with open(chemin, "r", encoding="utf-8") as f:
                        contenu = f.read()
                    match = re.search(r"<h1[^>]*>(.*?)</h1>", contenu, re.IGNORECASE | re.DOTALL)
                    nom = match.group(1).strip() if match else fichier
                    data = {"id": idx, "nom": nom, "html": contenu}
                    r = requests.post("http://localhost:5000/upload-fiche", json=data)
                    print(f"{fichier} → {r.text}")
                except Exception as e:
                    print(f"❌ Erreur upload {fichier}: {e}")
        threading.Thread(target=run, daemon=True).start()

    def list_fiches_api():
        def run():
            try:
                r = requests.get("http://localhost:5000/list-fiches")
                print(r.text)
            except Exception as e:
                print(f"❌ Erreur GET /list-fiches: {e}")
        threading.Thread(target=run, daemon=True).start()

    root = tk.Tk()
    root.title("WooCommerce Scraper")

    root.columnconfigure(0, weight=1)

    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, sticky="nsew")

    scraper_tab = ttk.Frame(notebook, padding=10)
    api_tab = ttk.Frame(notebook, padding=10)
    notebook.add(scraper_tab, text="Scraper")
    notebook.add(api_tab, text="API Flask")

    main_frame = scraper_tab
    main_frame.columnconfigure(0, weight=1)

    ttk.Label(main_frame, text="ID début").grid(row=0, column=0, sticky="w")
    ttk.Label(main_frame, text="ID fin").grid(row=0, column=1, sticky="w")

    start_var = tk.StringVar(value=id_list[0])
    end_var = tk.StringVar(value=id_list[-1])
    start_combo = ttk.Combobox(main_frame, values=id_list, textvariable=start_var, state="readonly", width=10)
    end_combo = ttk.Combobox(main_frame, values=id_list, textvariable=end_var, state="readonly", width=10)
    start_combo.grid(row=1, column=0, pady=5, sticky="ew")
    end_combo.grid(row=1, column=1, pady=5, sticky="ew")

    ttk.Label(main_frame, text="Dossier résultats").grid(row=2, column=0, sticky="w")
    entry_result = ttk.Entry(main_frame, width=25)
    entry_result.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

    chk_frame = ttk.Frame(main_frame)
    chk_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="w")
    var_variantes = tk.BooleanVar()
    var_concurrents = tk.BooleanVar()
    var_json = tk.BooleanVar()
    ttk.Checkbutton(chk_frame, text="Scraper les variantes produits", variable=var_variantes).grid(row=0, column=0, sticky="w")
    ttk.Checkbutton(chk_frame, text="Scraper les fiches produits concurrents", variable=var_concurrents).grid(row=1, column=0, sticky="w")
    ttk.Checkbutton(chk_frame, text="Exporter les JSON", variable=var_json).grid(row=2, column=0, sticky="w")

    base_dir_var = tk.StringVar(value=base_dir)

    def browse_folder():
        path = filedialog.askdirectory()
        if path:
            base_dir_var.set(path)

    ttk.Label(main_frame, text="Dossier de sortie").grid(row=5, column=0, sticky="w")
    base_dir_frame = ttk.Frame(main_frame)
    base_dir_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
    entry_base_dir = ttk.Entry(base_dir_frame, textvariable=base_dir_var, width=40)
    entry_base_dir.grid(row=0, column=0, sticky="ew")
    ttk.Button(base_dir_frame, text="Parcourir", command=browse_folder).grid(row=0, column=1, padx=5)
    ttk.Label(main_frame, textvariable=base_dir_var).grid(row=7, column=0, columnspan=2, sticky="w")

    action_frame = ttk.Frame(main_frame)
    action_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")
    action_frame.columnconfigure((0,1), weight=1)
    ttk.Button(action_frame, text="Lancer l'exécution", command=execute_actions).grid(row=0, column=0, padx=2, sticky="ew")
    ttk.Button(action_frame, text="Ouvrir dossier résultats", command=open_results_folder).grid(row=0, column=1, padx=2, sticky="ew")

    log_text = scrolledtext.ScrolledText(root, width=80, height=20, state="disabled")
    log_text.grid(row=1, column=0, columnspan=1, pady=10, sticky="nsew")
    root.rowconfigure(1, weight=1)

    status_var = tk.StringVar(value="")
    ttk.Label(root, textvariable=status_var).grid(row=2, column=0, sticky="w", padx=10)

    sys.stdout = TextRedirector(log_text)
    sys.stderr = TextRedirector(log_text)

    # === Widgets for API tab ===
    api_tab.columnconfigure(1, weight=1)
    ttk.Button(api_tab, text="Activer Flask", command=start_flask_server).grid(row=0, column=0, pady=5, sticky="w")

    ttk.Label(api_tab, text="Batch").grid(row=1, column=0, sticky="w")
    batch_var = tk.IntVar(value=1)
    batch_spin = ttk.Spinbox(api_tab, from_=1, to=999, textvariable=batch_var, width=5)
    batch_spin.grid(row=1, column=1, sticky="w")
    ttk.Button(api_tab, text="Charger un batch", command=load_batch).grid(row=1, column=2, padx=5)

    fiches_dir_var = tk.StringVar(value=os.path.join(base_dir, "fiche concurrents"))

    def browse_fiches_dir():
        path = filedialog.askdirectory()
        if path:
            fiches_dir_var.set(path)

    ttk.Label(api_tab, text="Dossier fiches").grid(row=2, column=0, sticky="w")
    ttk.Entry(api_tab, textvariable=fiches_dir_var, width=40).grid(row=2, column=1, sticky="ew")
    ttk.Button(api_tab, text="Parcourir", command=browse_fiches_dir).grid(row=2, column=2, padx=5)

    ttk.Button(api_tab, text="Uploader une fiche", command=upload_fiches).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
    ttk.Button(api_tab, text="Lister fiches", command=list_fiches_api).grid(row=3, column=2, pady=5, sticky="ew")

    root.mainloop()

