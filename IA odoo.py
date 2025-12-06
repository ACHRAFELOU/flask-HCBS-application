from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# -------------------------
# CONFIGURATION
# -------------------------
ODOO_URL = "https://mouwafaqa.anrt.ma/web/login"
USERNAME = "a.elouerghi@anrt.ma"
PASSWORD = "H-RAF2021@@"

# URL d'une demande Odoo
DEMANDE_URL = "https://mouwafaqa.anrt.ma/web#id=120350&model=anrt.solicitud.aprobacion&view_type=form&menu_id=83"

# Dossier où seront téléchargés les fichiers
DOSSIER = os.path.abspath("telechargements")
if not os.path.exists(DOSSIER):
    os.makedirs(DOSSIER)

# Options Chrome pour téléchargement automatique
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": DOSSIER,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})

# Lancer le driver Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # -------------------------
    # 1) LOGIN
    # -------------------------
    driver.get(ODOO_URL)
    time.sleep(3)

    driver.find_element(By.NAME, "login").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.ENTER)
    time.sleep(5)

    # -------------------------
    # 2) OUVRIR LA DEMANDE
    # -------------------------
    driver.get(DEMANDE_URL)
    time.sleep(5)

    # -------------------------
    # 3) OUVRIR L’ONGLET "Documents"
    # -------------------------
    onglet_docs = driver.find_element(By.XPATH, "//a[contains(text(),\"Documents\")]")
    onglet_docs.click()
    time.sleep(3)

    # -------------------------
    # 4) TROUVER TOUS LES BOUTONS PDF
    # -------------------------
    boutons_pdf = driver.find_elements(By.XPATH, "//i[contains(@class,'btn_Pre')]")

    if not boutons_pdf:
        print("❌ Aucun document PDF trouvé.")
        driver.quit()
        exit()

    print(f"📄 {len(boutons_pdf)} documents PDF trouvés.")

    # -------------------------
    # 5) TÉLÉCHARGER CHAQUE DOCUMENT
    # -------------------------
    for index in range(len(boutons_pdf)):
        # Recharger la liste à chaque tour (Odoo recharge parfois le DOM)
        boutons_pdf = driver.find_elements(By.XPATH, "//i[contains(@class,'btn_Pre')]")
        bouton = boutons_pdf[index]

        print(f"➡ Ouverture du document {index + 1}...")
        bouton.click()
        time.sleep(3)

        # Cliquer sur le bouton "Télécharger" dans la popup
        try:
            btn_dl = driver.find_element(By.XPATH, "//button[contains(@class,'o_download')]")
            btn_dl.click()
            print("⬇ Document téléchargé.")
        except:
            print("❌ Bouton de téléchargement introuvable pour ce document.")

        time.sleep(2)

        # Fermer la popup PDF si nécessaire
        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'Fermer') or contains(text(),'Close')]").click()
        except:
            pass

        time.sleep(2)

finally:
    print(f"✔ Tous les documents PDF sont téléchargés dans : {DOSSIER}")
    driver.quit()
