import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OdooDocumentDownloader:
    def __init__(self, odoo_url, username, password, demande_id):
        self.odoo_url = odoo_url
        self.username = username
        self.password = password
        self.demande_id = demande_id
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configure le driver Chrome avec les options appropriées"""
        chrome_options = Options()

        # Configuration pour télécharger automatiquement les PDFs
        prefs = {
            "download.default_directory": os.path.join(os.getcwd(), "downloads"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_settings.popups": 0,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Options pour éviter la détection comme bot
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Désactiver les logs du navigateur
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")

        # Initialiser le driver
        self.driver = webdriver.Chrome(options=chrome_options)

        # Masquer l'automation
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Masquer le webdriver
                Object.defineProperty(window, 'chrome', {
                    get: () => undefined
                });

                // Modifier les permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            '''
        })

        self.wait = WebDriverWait(self.driver, 20)

        # Créer le dossier de téléchargement s'il n'existe pas
        download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

    def login(self):
        """Connexion à Odoo"""
        logger.info("Connexion à Odoo...")
        try:
            self.driver.get(self.odoo_url)
            time.sleep(3)

            # Vérifier si déjà connecté
            current_url = self.driver.current_url
            if "web/login" not in current_url:
                logger.info("Déjà connecté")
                return True

            # Attendre et remplir le formulaire de connexion
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            password_input = self.driver.find_element(By.ID, "password")

            username_input.send_keys(self.username)
            password_input.send_keys(self.password)

            # Cliquer sur le bouton de connexion
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Attendre que la page se charge
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "o_menu_sections"))
            )
            logger.info("Connexion réussie")
            time.sleep(2)
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            raise

    def navigate_to_demande(self):
        """Navigation vers la demande spécifique - version améliorée"""
        logger.info(f"Navigation vers la demande ID: {self.demande_id}")

        # Construire l'URL directe de la demande
        demande_url = f"{self.odoo_url}/web#id={self.demande_id}&model=anrt.solicitud.aprobacion&view_type=form"

        logger.info(f"URL de la demande: {demande_url}")
        self.driver.get(demande_url)

        # Attendre que la page se charge complètement
        time.sleep(5)

        # Vérifier plusieurs éléments pour confirmer le chargement
        check_elements = [
            "//div[contains(@class, 'o_form_view')]",
            "//span[contains(@class, 'numero_solicitud')]",
            "//li[@class='breadcrumb-item active']",
            "//div[contains(@class, 'o_notebook')]"
        ]

        for element in check_elements:
            try:
                self.driver.find_element(By.XPATH, element)
                logger.info(f"Élément de confirmation trouvé: {element}")
                break
            except:
                continue

        logger.info("Page de la demande chargée")
        time.sleep(2)
        return True

    def click_ouverture(self):
        """Cliquer sur le bouton 'Ouverture' si disponible"""
        logger.info("Recherche du bouton 'Ouverture'...")
        try:
            # Chercher le bouton Ouverture
            ouverture_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@name, 'ouverture')]"))
            )

            if ouverture_button.is_displayed():
                logger.info("Bouton Ouverture trouvé et visible")
                ouverture_button.click()
                logger.info("Bouton 'Ouverture' cliqué")
                time.sleep(3)

                # Vérifier que quelque chose a changé
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(@name, 'soumise_a_anrt')]"))
                    )
                    logger.info("Vérification: bouton 'Soumise à l'ANRT' trouvé")
                except:
                    logger.info("Pas de changement détecté après clic sur Ouverture")

                return True
            else:
                logger.warning("Bouton Ouverture trouvé mais non visible")
                return False

        except Exception as e:
            logger.warning(f"Bouton Ouverture non trouvé ou non cliquable: {e}")
            return False

    def navigate_to_documents_tab_smart(self):
        """Navigation intelligente vers l'onglet Documents"""
        logger.info("Navigation intelligente vers l'onglet Documents...")

        # Prendre une capture d'écran avant
        self.take_screenshot("avant_navigation_documents")

        # Stratégie 1: Utiliser JavaScript pour trouver et cliquer sur l'onglet Documents
        logger.info("Stratégie 1: Utilisation de JavaScript")
        try:
            result = self.driver.execute_script("""
                // Fonction pour trouver et cliquer sur l'onglet Documents
                function findAndClickDocumentsTab() {
                    console.log("Recherche de l'onglet Documents...");

                    // Chercher tous les onglets
                    const tabs = document.querySelectorAll('.nav-tabs a, .nav-tabs li a, [role="tab"]');
                    console.log("Nombre d'onglets trouvés:", tabs.length);

                    // Afficher tous les onglets pour débogage
                    for (let i = 0; i < tabs.length; i++) {
                        console.log(`Onglet ${i}: texte="${tabs[i].textContent.trim()}", href="${tabs[i].getAttribute('href')}"`);
                    }

                    // Chercher l'onglet Documents par texte
                    for (let tab of tabs) {
                        const text = tab.textContent || tab.innerText || "";
                        if (text.toLowerCase().includes('document')) {
                            console.log("Onglet Documents trouvé par texte:", text);

                            // Vérifier si l'onglet est déjà actif
                            const parentLi = tab.closest('li');
                            if (parentLi && parentLi.classList.contains('active')) {
                                console.log("L'onglet Documents est déjà actif");
                                return {success: true, alreadyActive: true};
                            }

                            // Simuler un clic
                            tab.click();
                            console.log("Clic sur l'onglet Documents");
                            return {success: true, alreadyActive: false};
                        }
                    }

                    // Si non trouvé par texte, chercher par position (2ème onglet)
                    if (tabs.length >= 2) {
                        const secondTab = tabs[1];
                        console.log("Clique sur le 2ème onglet:", secondTab.textContent);
                        secondTab.click();
                        return {success: true, alreadyActive: false};
                    }

                    return {success: false, error: "Onglet Documents non trouvé"};
                }

                return findAndClickDocumentsTab();
            """)

            if result.get('success'):
                logger.info("JavaScript: Navigation vers Documents réussie")
                time.sleep(3)

                # Vérifier si le contenu des documents est chargé
                if self.wait_for_documents_content():
                    return True
                else:
                    logger.warning("JavaScript: Le contenu des documents n'est pas apparu")
                    # Continuer avec d'autres stratégies
            else:
                logger.warning(f"JavaScript: Échec - {result.get('error')}")

        except Exception as e:
            logger.error(f"Erreur JavaScript: {e}")

        # Stratégie 2: Utiliser Selenium pour trouver l'onglet
        logger.info("Stratégie 2: Recherche avec Selenium")
        try:
            # Chercher tous les onglets
            tabs = self.driver.find_elements(By.XPATH,
                                             "//ul[contains(@class, 'nav-tabs')]//a | //ul[contains(@class, 'nav')]//a[contains(@class, 'nav-link')]"
                                             )

            logger.info(f"Nombre d'onglets trouvés avec Selenium: {len(tabs)}")

            if not tabs:
                logger.error("Aucun onglet trouvé")
                return False

            # Afficher les onglets pour débogage
            for i, tab in enumerate(tabs):
                try:
                    text = tab.text.strip()
                    href = tab.get_attribute('href') or tab.get_attribute('data-href') or ''
                    logger.info(f"Onglet {i}: '{text}' - href: {href}")
                except:
                    logger.info(f"Onglet {i}: [erreur lors de la lecture]")

            # Chercher l'onglet Documents
            documents_tab = None
            for tab in tabs:
                try:
                    text = tab.text.strip().lower()
                    if 'document' in text:
                        documents_tab = tab
                        logger.info(f"Onglet Documents trouvé par texte: '{tab.text.strip()}'")
                        break
                except:
                    continue

            # Si non trouvé, prendre le 2ème onglet
            if not documents_tab and len(tabs) >= 2:
                documents_tab = tabs[1]
                logger.info(f"Utilisation du 2ème onglet: '{documents_tab.text.strip()}'")

            if documents_tab:
                # Essayer de cliquer
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", documents_tab)
                    time.sleep(1)

                    # Essayer plusieurs méthodes de clic
                    try:
                        documents_tab.click()
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click();", documents_tab)

                    logger.info("Clic sur l'onglet")
                    time.sleep(3)

                    # Vérifier le contenu
                    if self.wait_for_documents_content():
                        return True

                except Exception as e:
                    logger.error(f"Erreur lors du clic sur l'onglet: {e}")

        except Exception as e:
            logger.error(f"Erreur stratégie Selenium: {e}")

        # Stratégie 3: Navigation directe via URL
        logger.info("Stratégie 3: Navigation par URL directe")
        try:
            # Essayer différentes URL possibles pour l'onglet Documents
            base_url = self.driver.current_url.split('#')[0]

            # URL possibles pour Documents
            possible_urls = [
                f"{base_url}#notebook_page_130",  # ID du HTML fourni
                f"{base_url}#notebook_page_128",  # ID précédent
                f"{base_url}#notebook_page_131",  # Autre ID possible
                f"{base_url}#view_type=form&model=anrt.solicitud.aprobacion&id={self.demande_id}&active_id=2"
            ]

            for url in possible_urls:
                try:
                    logger.info(f"Essai d'accès à: {url}")
                    self.driver.get(url)
                    time.sleep(4)

                    if self.wait_for_documents_content():
                        logger.info(f"Navigation directe réussie avec: {url}")
                        return True

                except Exception as e:
                    logger.debug(f"Échec avec URL {url}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Erreur stratégie URL: {e}")

        # Si toutes les stratégies échouent
        logger.error("Toutes les stratégies de navigation vers Documents ont échoué")
        self.take_screenshot("echec_navigation_documents")
        return False

    def wait_for_documents_content(self, timeout=10):
        """Attendre que le contenu des documents soit chargé"""
        logger.info("Attente du contenu des documents...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Chercher plusieurs indicateurs de contenu des documents
                indicators = [
                    "//div[contains(text(), 'Documents requis')]",
                    "//th[contains(text(), 'Nom du fichier')]",
                    "//button[contains(@class, 'btn_Pre')]",
                    "//td[contains(@class, 'name_doc')]",
                    "//table[contains(@class, 'o_list_view')]//tbody//tr[.//button]"
                ]

                for indicator in indicators:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements:
                        logger.info(f"Contenu des documents détecté avec: {indicator} ({len(elements)} éléments)")
                        return True

                # Vérifier aussi par le titre actif
                try:
                    active_tab = self.driver.find_element(By.XPATH,
                                                          "//li[contains(@class, 'active')]//a[contains(@class, 'nav-link')]"
                                                          )
                    tab_text = active_tab.text.strip().lower()
                    if 'document' in tab_text:
                        logger.info(f"Onglet actif est '{active_tab.text.strip()}'")
                        return True
                except:
                    pass

                time.sleep(1)

            except Exception as e:
                logger.debug(f"Erreur lors de la vérification: {e}")
                time.sleep(1)

        logger.warning(f"Timeout après {timeout} secondes - contenu des documents non détecté")
        return False

    def extract_document_ids_with_javascript(self):
        """Extraire les IDs des documents depuis les lignes de la table"""
        logger.info("Extraction des IDs des documents via JavaScript...")

        try:
            # Exécuter JavaScript pour extraire les IDs et noms des documents
            documents_data = self.driver.execute_script("""
                var documents = [];
                var rows = document.querySelectorAll('table.o_list_view tbody tr.o_data_row');

                for (var i = 0; i < rows.length; i++) {
                    var row = rows[i];

                    // Trouver l'ID du document (peut être caché)
                    var idElement = row.querySelector('.id_doc');
                    var id = '';
                    if (idElement) {
                        id = idElement.textContent.trim();
                    }

                    // Trouver le nom du fichier
                    var nameElement = row.querySelector('.name_doc');
                    var filename = '';
                    if (nameElement) {
                        filename = nameElement.textContent.trim();
                    }

                    // Trouver le bouton de prévisualisation
                    var button = row.querySelector('.btn_Pre');

                    if (id || filename) {
                        documents.push({
                            id: id || 'unknown_' + i,
                            filename: filename || 'document_' + i + '.pdf',
                            rowIndex: i,
                            button: button
                        });
                    }
                }

                return documents;
            """)

            logger.info(f"Données extraites pour {len(documents_data)} documents")
            return documents_data

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des IDs: {e}")
            return []

    def download_all_documents_modal_optimized(self):
        """Télécharger tous les documents via les modals - version optimisée"""
        logger.info("Téléchargement optimisé des documents via les modals...")

        try:
            # Attendre que les documents soient visibles
            if not self.wait_for_documents_content():
                logger.error("Contenu des documents non chargé")
                return False

            time.sleep(2)

            # Extraire les données des documents via JavaScript
            documents_data = self.extract_document_ids_with_javascript()

            if not documents_data:
                logger.warning("Aucune donnée de document extraite")
                # Fallback: trouver les boutons normalement
                preview_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'btn_Pre')]")
                documents_data = []
                for i, button in enumerate(preview_buttons):
                    documents_data.append({
                        'id': f'unknown_{i}',
                        'filename': f'document_{i}.pdf',
                        'rowIndex': i,
                        'button': button
                    })

            logger.info(f"Nombre de documents à traiter: {len(documents_data)}")

            downloaded_count = 0
            failed_documents = []

            # Méthode 1: Tenter de télécharger directement via les IDs
            logger.info("Tentative de téléchargement direct via les IDs...")
            for doc_data in documents_data:
                try:
                    doc_id = doc_data['id']
                    filename = doc_data['filename']

                    # Nettoyer le nom de fichier
                    clean_filename = self.clean_filename(filename)

                    # Construire l'URL de téléchargement selon le pattern du JavaScript
                    download_url = f"{self.odoo_url}/web/content/anrt.documento.req/{doc_id}/fichier/{filename}"

                    logger.info(f"Tentative de téléchargement direct pour: {clean_filename}")
                    logger.info(f"URL: {download_url}")

                    # Télécharger via JavaScript
                    if self.download_file_via_js(download_url, clean_filename):
                        downloaded_count += 1
                        logger.info(f"✓ Document téléchargé: {clean_filename}")
                        time.sleep(1)  # Pause courte entre les téléchargements
                    else:
                        logger.warning(f"✗ Échec du téléchargement direct pour: {clean_filename}")
                        failed_documents.append(doc_data)

                except Exception as e:
                    logger.error(f"Erreur avec le document {doc_data.get('filename', 'inconnu')}: {e}")
                    failed_documents.append(doc_data)

            # Méthode 2: Pour les échecs, utiliser la méthode par modal
            if failed_documents:
                logger.info(f"Tentative via les modals pour {len(failed_documents)} documents ayant échoué...")

                for doc_data in failed_documents:
                    try:
                        logger.info(f"Traitement via modal: {doc_data.get('filename', 'inconnu')}")

                        # Cliquer sur le bouton pour ouvrir la modal
                        button = doc_data.get('button')
                        if button:
                            try:
                                self.driver.execute_script("arguments[0].click();", button)
                                time.sleep(2)  # Attendre que la modal s'ouvre

                                # Télécharger depuis la modal
                                if self.download_from_modal_optimized():
                                    downloaded_count += 1
                                    logger.info(f"✓ Document téléchargé via modal")
                                else:
                                    logger.warning(f"✗ Échec du téléchargement via modal")

                                # Fermer la modal
                                self.close_modal_if_open()
                                time.sleep(1)

                            except Exception as e:
                                logger.error(f"Erreur avec le bouton: {e}")
                        else:
                            logger.warning("Bouton non trouvé pour ce document")

                    except Exception as e:
                        logger.error(f"Erreur lors du traitement via modal: {e}")

            logger.info(
                f"Téléchargement terminé. {downloaded_count}/{len(documents_data)} documents téléchargés avec succès")
            return downloaded_count > 0

        except Exception as e:
            logger.error(f"Erreur lors du téléchargement optimisé: {e}")
            return False

    def download_from_modal_optimized(self):
        """Télécharger le fichier depuis la modal ouverte - version optimisée"""
        try:
            # Attendre que la modal soit complètement chargée
            time.sleep(1)

            # Chercher le lien de téléchargement dans la modal
            download_link = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'modal-dialog')]//a[contains(@class, 'fa-download')]"))
            )

            # Récupérer le texte du lien (contient le nom du fichier)
            link_text = download_link.text.strip()

            # Extraire le nom du fichier
            filename = link_text
            if ' ' in link_text:
                # Le format est généralement: "📄 nom_du_fichier.pdf"
                filename = link_text.split(' ', 1)[1] if ' ' in link_text else link_text

            # Nettoyer le nom de fichier
            clean_filename = self.clean_filename(filename)

            logger.info(f"Téléchargement depuis la modal: {clean_filename}")

            # Utiliser JavaScript pour cliquer sur le lien
            self.driver.execute_script("arguments[0].click();", download_link)

            time.sleep(2)  # Attendre le début du téléchargement

            logger.info(f"✓ Fichier en cours de téléchargement: {clean_filename}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du téléchargement depuis la modal: {e}")
            return False

    def download_file_via_js(self, url, filename):
        """Télécharger un fichier via JavaScript"""
        try:
            # Nettoyer l'URL
            clean_url = url.replace("'", "\\'").replace('"', '\\"')
            clean_filename = filename.replace("'", "\\'").replace('"', '\\"')

            # Utiliser JavaScript pour télécharger le fichier
            script = f"""
                try {{
                    var link = document.createElement('a');
                    link.href = '{clean_url}';
                    link.download = '{clean_filename}';
                    link.target = '_blank';
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    console.log('Téléchargement déclenché pour:', '{clean_filename}');
                    return true;
                }} catch (e) {{
                    console.error('Erreur lors du téléchargement:', e);
                    return false;
                }}
            """

            result = self.driver.execute_script(script)
            if result:
                logger.debug(f"Téléchargement déclenché via JS pour: {filename}")
                time.sleep(2)  # Attendre le téléchargement
                return True
            else:
                logger.warning(f"Échec du téléchargement via JS pour: {filename}")
                return False

        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de {filename}: {e}")
            return False

    def clean_filename(self, filename):
        """Nettoyer le nom de fichier pour qu'il soit valide"""
        # Remplacer les caractères problématiques
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        clean_name = filename
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')

        # Limiter la longueur si nécessaire
        if len(clean_name) > 200:
            name, ext = os.path.splitext(clean_name)
            clean_name = name[:200 - len(ext)] + ext

        return clean_name

    def close_modal_if_open(self):
        """Fermer la modal si elle est ouverte"""
        try:
            # Chercher le bouton de fermeture de la modal
            close_buttons = self.driver.find_elements(By.XPATH,
                                                      "//div[contains(@class, 'modal-dialog')]//button[contains(@class, 'close') or contains(@class, 'o_form_button_cancel') or contains(text(), 'Fermer')]"
                                                      )

            if close_buttons:
                for button in close_buttons:
                    try:
                        if button.is_displayed():
                            logger.debug("Fermeture de la modal...")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            break
                    except:
                        continue

        except Exception as e:
            logger.debug(f"Erreur lors de la fermeture de la modal: {e}")

    def take_screenshot(self, name):
        """Prendre une capture d'écran"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"Capture d'écran sauvegardée: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Erreur lors de la capture d'écran: {e}")
            return None

    def run(self):
        """Exécuter le processus complet"""
        try:
            logger.info("=" * 70)
            logger.info(f"DEBUT DU PROCESSUS - Demande ID: {self.demande_id}")
            logger.info("=" * 70)

            # 1. Configuration
            logger.info("Étape 1: Configuration du navigateur")
            self.setup_driver()

            # 2. Connexion
            logger.info("Étape 2: Connexion à Odoo")
            if not self.login():
                logger.error("Échec de la connexion")
                return

            # 3. Navigation vers la demande
            logger.info(f"Étape 3: Navigation vers la demande {self.demande_id}")
            if not self.navigate_to_demande():
                logger.error("Échec de la navigation vers la demande")
                return

            # Prendre une capture d'écran de la page de la demande
            self.take_screenshot("page_demande")

            # 4. Clic sur Ouverture (optionnel)
            logger.info("Étape 4: Tentative de clic sur 'Ouverture'")
            self.click_ouverture()
            time.sleep(3)

            # 5. Navigation vers l'onglet Documents
            logger.info("Étape 5: Navigation vers l'onglet Documents")
            self.take_screenshot("avant_documents")

            if not self.navigate_to_documents_tab_smart():
                logger.error("Échec critique: impossible d'accéder à l'onglet Documents")
                logger.info("Tentative de téléchargement direct sans navigation...")

            # Prendre une capture d'écran après navigation
            self.take_screenshot("apres_navigation_documents")

            # 6. Téléchargement des documents via les modals
            logger.info("Étape 6: Téléchargement des documents optimisé")
            self.download_all_documents_modal_optimized()

            logger.info("=" * 70)
            logger.info("PROCESSUS TERMINÉ")
            logger.info("=" * 70)

            # Attendre avant de fermer pour vérifier les téléchargements
            logger.info("Attente de 10 secondes avant fermeture...")
            time.sleep(10)

        except Exception as e:
            logger.error(f"ERREUR DANS LE PROCESSUS: {e}", exc_info=True)
            self.take_screenshot("erreur_finale")

        finally:
            # Fermer le navigateur
            if self.driver:
                logger.info("Fermeture du navigateur")
                try:
                    self.driver.quit()
                except:
                    pass


if __name__ == "__main__":
    # Configuration
    ODOO_URL = "https://mouwafaqa.anrt.ma"
    USERNAME = "a.elouerghi@anrt.ma"
    PASSWORD = "H-RAF2021@@"
    DEMANDE_ID = "120777"

    # Exécuter le téléchargement
    downloader = OdooDocumentDownloader(ODOO_URL, USERNAME, PASSWORD, DEMANDE_ID)
    downloader.run()