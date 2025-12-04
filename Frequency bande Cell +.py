from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# -------------------------
# CONFIGURATION
# -------------------------
ODOO_URL = "https://mouwafaqa.anrt.ma"
USERNAME = "a.elouerghi@anrt.ma"
PASSWORD = "H-RAF2021@@"
DEMANDE_ID = "120614"

# Nouvelles fréquences à définir - DOUZE LIGNES avec puissances
NOUVELLES_FREQUENCES = [
    # Ligne 1: WiFi 2.4 GHz
    {
        "freq_emission_min": "2400",
        "freq_emission_max": "2483.5",
        "freq_reception_min": "2400",
        "freq_reception_max": "2483.5",
        "puissance": "20",  # Valeur de puissance
        "unite_puissance": "dBm"  # Unité de puissance
    },
    # Ligne 2: Bluetooth 2.4 GHz
    {
        "freq_emission_min": "2400",
        "freq_emission_max": "2483.5",
        "freq_reception_min": "2400",
        "freq_reception_max": "2483.5",
        "puissance": "13",  # Valeur de puissance
        "unite_puissance": "dBm"  # Unité de puissance
    },
    # Ligne 3: WiFi 5 GHz
    {
        "freq_emission_min": "5150",
        "freq_emission_max": "5350",
        "freq_reception_min": "5150",
        "freq_reception_max": "5350",
        "puissance": "23",  # Valeur de puissance
        "unite_puissance": "dBm"  # Unité de puissance
    },
    # Ligne 4: WiFi 6E
    {
        "freq_emission_min": "5925",
        "freq_emission_max": "6425",
        "freq_reception_min": "5925",
        "freq_reception_max": "6425",
        "puissance": "23",  # Valeur de puissance
        "unite_puissance": "dBm"  # Unité de puissance
    },
    # Ligne 5: RFID
    {
        "freq_emission_min": "13.56",
        "freq_emission_max": "13.56",
        "freq_reception_min": "13.56",
        "freq_reception_max": "13.56",
        "puissance": "60",  # Valeur de puissance
        "unite_puissance": "dBm"  # Unité de puissance
    },
    # Ligne 6: GSM 900 (Puissance 33 dBm)
    {
        "freq_emission_min": "880",
        "freq_emission_max": "915",
        "freq_reception_min": "925",
        "freq_reception_max": "960",
        "puissance": "33.0",  # Valeur de puissance
        "unite_puissance": "W"  # Unité de puissance
    },
    # Ligne 7: GSM 1800 (Puissance 30 dBm)
    {
        "freq_emission_min": "1710",
        "freq_emission_max": "1785",
        "freq_reception_min": "1805",
        "freq_reception_max": "1880",
        "puissance": "30.0",
        "unite_puissance": "W"
    },
    # Ligne 8: LTE 800 (Puissance 23 dBm)
    {
        "freq_emission_min": "832",
        "freq_emission_max": "862",
        "freq_reception_min": "791",
        "freq_reception_max": "821",
        "puissance": "23.0",
        "unite_puissance": "W"
    },
    # Ligne 9: LTE 1800 (Puissance 23 dBm)
    {
        "freq_emission_min": "1710",
        "freq_emission_max": "1785",
        "freq_reception_min": "1805",
        "freq_reception_max": "1880",
        "puissance": "23.0",
        "unite_puissance": "W"
    },
    # Ligne 10: LTE 2600 (Puissance 23 dBm)
    {
        "freq_emission_min": "2500",
        "freq_emission_max": "2570",
        "freq_reception_min": "2620",
        "freq_reception_max": "2690",
        "puissance": "23.0",
        "unite_puissance": "W"
    },
    # Ligne 11: UMTS 900 (Puissance 24 dBm)
    {
        "freq_emission_min": "880",
        "freq_emission_max": "915",
        "freq_reception_min": "925",
        "freq_reception_max": "960",
        "puissance": "24.0",
        "unite_puissance": "W"
    },
    # Ligne 12: UMTS 2100 (Puissance 24 dBm)
    {
        "freq_emission_min": "1920",
        "freq_emission_max": "1980",
        "freq_reception_min": "2110",
        "freq_reception_max": "2170",
        "puissance": "24.0",
        "unite_puissance": "W"
    }
]


# -------------------------
# FONCTIONS UTILITAIRES
# -------------------------
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def login_to_odoo(driver):
    print("🔐 Connexion à Odoo...")
    driver.get(f"{ODOO_URL}/web/login")
    time.sleep(3)

    # Vérifier si déjà connecté
    if "web/login" not in driver.current_url:
        print("✓ Déjà connecté")
        return True

    driver.find_element(By.NAME, "login").send_keys(USERNAME)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)

    if "web" in driver.current_url:
        print("✓ Connexion réussie")
        return True
    else:
        print("❌ Échec de connexion")
        return False


def navigate_to_demand(driver):
    print(f"📍 Navigation vers la demande {DEMANDE_ID}...")
    url = f"{ODOO_URL}/web#id={DEMANDE_ID}&model=anrt.solicitud.aprobacion&view_type=form&menu_id=83"
    driver.get(url)
    time.sleep(5)

    # Attendre que la page charge
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".o_form_view"))
        )
        print("✓ Page de demande chargée")
        return True
    except:
        print("⚠️ La page de demande pourrait ne pas être chargée correctement")
        return True


def find_and_click_edit_button(driver):
    """Trouve et clique sur le bouton d'édition"""
    print("🔍 Recherche du bouton d'édition...")

    # Méthode 1: Par classe
    try:
        btn = driver.find_element(By.CSS_SELECTOR, ".o_form_button_edit")
        if btn.is_displayed():
            btn.click()
            print("✓ Mode édition activé")
            time.sleep(2)
            return True
    except:
        pass

    # Méthode 2: Par texte
    try:
        edit_buttons = driver.find_elements(By.XPATH,
                                            "//button[contains(text(), 'Edit') or contains(text(), 'Éditer') or contains(text(), 'Modifier')]")
        for btn in edit_buttons:
            if btn.is_displayed():
                btn.click()
                print("✓ Mode édition activé (texte)")
                time.sleep(2)
                return True
    except:
        pass

    # Méthode 3: Vérifier si déjà en mode édition
    try:
        if driver.execute_script("return document.querySelector('.o_form_editable') !== null"):
            print("✓ Déjà en mode édition")
            return True
    except:
        pass

    print("⚠️ Impossible de trouver le bouton d'édition")
    return False


def open_radio_technology_section(driver):
    """Ouvre la section Technologie radio en cliquant dessus"""
    print("\n🔧 Ouverture de la section Technologie radio...")

    # Chercher la section par différents moyens
    section_selectors = [
        "//label[contains(text(), 'Technologie radio') or contains(text(), 'Technologie Radio') or contains(text(), 'Radio Technology')]",
        "//div[contains(text(), 'Technologie radio') or contains(text(), 'Technologie Radio')]",
        "//span[contains(text(), 'Technologie radio') or contains(text(), 'Technologie Radio')]",
        "//*[contains(@class, 'technologie') or contains(@class, 'radio')]//label",
        "//div[contains(@class, 'o_field_widget') and contains(@name, 'technologie')]"
    ]

    for selector in section_selectors:
        try:
            sections = driver.find_elements(By.XPATH, selector)
            for section in sections:
                if section.is_displayed():
                    print(f"✓ Section trouvée avec: {selector}")

                    # Essayer de cliquer sur la section
                    try:
                        section.click()
                        print("✓ Section cliquée")
                        time.sleep(2)
                        return True
                    except:
                        # Essayer de cliquer sur le parent
                        try:
                            parent = section.find_element(By.XPATH,
                                                          "./ancestor::div[contains(@class, 'o_field_widget') or contains(@class, 'o_group')]")
                            parent.click()
                            print("✓ Parent de la section cliqué")
                            time.sleep(2)
                            return True
                        except:
                            pass
        except:
            continue

    # Si aucune section n'est trouvée, essayer JavaScript
    print("🔄 Tentative avec JavaScript...")
    try:
        result = driver.execute_script("""
            // Chercher tous les éléments contenant "Technologie radio"
            var elements = document.querySelectorAll('label, div, span, h1, h2, h3, h4');
            for(var elem of elements) {
                var text = elem.textContent || elem.innerText || '';
                if(text.includes('Technologie radio') || text.includes('Technologie Radio') || text.includes('Radio Technology')) {
                    elem.click();
                    console.log('Section Technologie radio cliquée via JS');

                    // Simuler aussi un clic sur le parent
                    var parent = elem.closest('.o_field_widget, .o_group, .o_notebook_page');
                    if(parent) {
                        parent.click();
                    }

                    return true;
                }
            }
            return false;
        """)

        if result:
            print("✓ Section ouverte via JavaScript")
            time.sleep(2)
            return True
    except Exception as e:
        print(f"⚠️ Erreur JavaScript: {e}")

    print("⚠️ Impossible d'ouvrir la section Technologie radio")
    return False


def open_frequency_lines(driver, num_lines):
    """Ouvre chaque ligne de fréquence pour accéder aux champs"""
    print(f"\n📋 Ouverture des {num_lines} ligne(s) de fréquence...")

    try:
        # Chercher les lignes de fréquence
        line_selectors = [
            "//tr[contains(@class, 'o_data_row')]",
            "//div[contains(@class, 'o_list_view')]//tr",
            "//table[contains(@class, 'o_list_view')]//tr[position()>1]",
            "//*[contains(text(), 'Bande') or contains(text(), 'bande')]/ancestor::tr",
            "//tr[.//*[contains(text(), 'MHz') or contains(text(), 'freq')]]"
        ]

        lines_opened = 0

        for line_index in range(num_lines):
            print(f"  Ouverture ligne {line_index + 1}...")

            for selector in line_selectors:
                try:
                    lines = driver.find_elements(By.XPATH, selector)
                    if line_index < len(lines):
                        line = lines[line_index]

                        if line.is_displayed():
                            # Cliquer sur la ligne pour l'ouvrir
                            line.click()
                            print(f"    ✓ Ligne {line_index + 1} cliquée")
                            time.sleep(1)
                            lines_opened += 1
                            break
                except:
                    continue

            # Si aucune ligne n'a été trouvée avec les sélecteurs, essayer JavaScript
            if lines_opened <= line_index:
                print(f"    🔄 Tentative JavaScript pour ligne {line_index + 1}...")
                result = driver.execute_script(f"""
                    // Chercher toutes les lignes de table
                    var rows = document.querySelectorAll('tr');
                    var freqRows = [];

                    for(var i = 0; i < rows.length; i++) {{
                        var row = rows[i];
                        if(row.style.display !== 'none' && row.offsetHeight > 0) {{
                            // Vérifier si c'est une ligne de données
                            var text = row.textContent || row.innerText || '';
                            if(text.includes('MHz') || text.includes('freq') || text.includes('banda') || 
                               row.classList.contains('o_data_row') || row.getAttribute('data-id')) {{
                                freqRows.push(row);
                            }}
                        }}
                    }}

                    // Cliquer sur la ligne demandée
                    if({line_index} < freqRows.length) {{
                        freqRows[{line_index}].click();
                        console.log('Ligne {line_index + 1} cliquée via JS');
                        return true;
                    }}
                    return false;
                """)

                if result:
                    print(f"    ✓ Ligne {line_index + 1} ouverte via JavaScript")
                    lines_opened += 1
                    time.sleep(1)

            # Petite pause entre les lignes
            time.sleep(0.5)

        print(f"✓ {lines_opened} ligne(s) ouverte(s)")
        return lines_opened > 0

    except Exception as e:
        print(f"⚠️ Erreur ouverture lignes: {e}")
        return False


def wait_for_manual_save(line_index, total_lines):
    """Attend que l'utilisateur clique manuellement sur Sauvegarder"""
    print(f"\n⏳ PAUSE INTERACTIVE - Ligne {line_index}/{total_lines}")
    print("=" * 50)
    print("📝 INSTRUCTIONS:")
    print("1. Vérifiez que tous les champs (fréquences et puissance) sont correctement remplis")
    print("2. Cliquez manuellement sur le bouton 'Sauvegarder'")
    print("3. Attendez que la sauvegarde se termine")
    print("4. Revenez à ce script et appuyez sur Entrée pour continuer")
    print("=" * 50)

    input("Appuyez sur Entrée pour continuer avec la ligne suivante...")
    print("✓ Reprise du script...")
    time.sleep(2)
    return True


def wait_before_line(line_index, total_lines):
    """Pause avant de commencer à modifier une ligne"""
    print(f"\n⏳ PRÉPARATION - Ligne {line_index}/{total_lines}")
    print("=" * 50)
    print("📝 INSTRUCTIONS:")
    print(f"1. Préparez-vous à modifier la ligne {line_index}")
    print("2. Assurez-vous que la section 'Technologie radio' est ouverte")
    print("3. La ligne doit être accessible pour modification")
    print("=" * 50)

    input("Appuyez sur Entrée pour commencer la modification de cette ligne...")
    print("✓ Début de la modification...")
    time.sleep(2)
    return True


def modify_power_field(driver, line_index, puissance_value, unite_puissance):
    """Modifie le champ de puissance pour une ligne spécifique"""
    print(f"\n    ⚡ Modification de la puissance: {puissance_value} {unite_puissance}")

    try:
        # Méthode 1: Chercher par nom 'tr_potencia' comme dans l'HTML fourni
        power_selectors = [
            ("//span[@name='tr_potencia']", "span"),
            ("//*[@name='tr_potencia']", "any"),
            ("//span[contains(@class, 'o_field_char') and contains(@class, 'tr_potencia')]", "span"),
            ("//*[contains(@name, 'potencia')]", "any"),
            ("//*[contains(@class, 'tr_potencia')]", "any")
        ]

        for selector, elem_type in power_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    # Si plusieurs éléments, prendre celui correspondant à la ligne
                    if line_index < len(elements):
                        elem = elements[line_index]
                    else:
                        elem = elements[0]  # Prendre le premier si pas assez d'éléments

                    if elem.is_displayed():
                        # Pour les champs Odoo, on peut souvent cliquer puis écrire
                        elem.click()
                        time.sleep(0.5)

                        # Nettoyer le champ et entrer la nouvelle valeur
                        # Différentes approches selon le type de champ
                        if elem.tag_name == "input":
                            elem.clear()
                            elem.send_keys(puissance_value)
                        else:
                            # Pour les spans ou autres éléments, utiliser JavaScript
                            driver.execute_script("""
                                arguments[0].innerText = arguments[1];
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            """, elem, puissance_value)

                        print(f"    ✓ Puissance modifiée: {puissance_value}")

                        # Déclencher un événement blur pour sauvegarder
                        elem.send_keys("\t")  # Tab pour sortir du champ
                        time.sleep(0.5)

                        return True
            except:
                continue

        # Méthode 2: JavaScript pour trouver le champ puissance
        print(f"    🔄 Tentative JavaScript pour la puissance...")
        js_find_power = """
            var lineIndex = arguments[0];
            var newPower = arguments[1];
            
            // Chercher tous les champs puissance
            var powerFields = [];
            var allElements = document.querySelectorAll('*[name*="potencia"], *[class*="potencia"], span.o_field_char');
            
            for(var elem of allElements) {
                var name = elem.getAttribute('name') || '';
                var className = elem.className || '';
                var text = elem.textContent || '';
                
                if(name.includes('potencia') || className.includes('potencia') || 
                   (elem.tagName === 'SPAN' && elem.classList.contains('o_field_char') && text.match(/\\d+\\.\\d+/))) {
                    powerFields.push(elem);
                }
            }
            
            // Sélectionner le bon champ selon l'index de ligne
            if(lineIndex < powerFields.length) {
                var field = powerFields[lineIndex];
                field.textContent = newPower;
                
                // Déclencher les événements
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
                
                return true;
            }
            
            return false;
        """

        result = driver.execute_script(js_find_power, line_index, puissance_value)
        if result:
            print(f"    ✓ Puissance modifiée via JS: {puissance_value}")
            return True

        # Méthode 3: Recherche par texte et contexte
        print(f"    🔍 Recherche avancée pour le champ puissance...")
        try:
            # Chercher près des labels "Puissance" ou "Potencia"
            power_labels = driver.find_elements(By.XPATH,
                "//label[contains(text(), 'Puissance') or contains(text(), 'Potencia') or contains(text(), 'Power')]")

            for label in power_labels:
                if label.is_displayed():
                    # Essayer de trouver le champ associé
                    try:
                        # Chercher l'élément frère suivant ou parent
                        field = driver.execute_script("""
                            var label = arguments[0];
                            // Chercher dans le même TD ou div parent
                            var parentRow = label.closest('tr, div, td');
                            if(parentRow) {
                                var spans = parentRow.querySelectorAll('span.o_field_char, span[name*="potencia"]');
                                for(var span of spans) {
                                    if(span.textContent && span.textContent.match(/\\d+\\.?\\d*/)) {
                                        return span;
                                    }
                                }
                            }
                            return null;
                        """, label)

                        if field:
                            field.click()
                            field.clear()
                            driver.execute_script("arguments[0].textContent = arguments[1];", field, puissance_value)
                            field.send_keys("\t")
                            print(f"    ✓ Puissance trouvée par label: {puissance_value}")
                            return True
                    except:
                        continue

        except Exception as e:
            print(f"    ⚠️ Erreur recherche par label: {e}")

        print(f"    ⚠️ Champ puissance non trouvé pour la ligne {line_index + 1}")
        return False

    except Exception as e:
        print(f"    ❌ Erreur modification puissance: {e}")
        return False


def modify_frequency_fields_with_pauses(driver):
    """Modifie les champs de fréquence et puissance avec pauses interactives"""
    print("\n📡 Modification des fréquences radio avec pauses...")

    try:
        # 1. Ouvrir la section Technologie radio
        if not open_radio_technology_section(driver):
            print("⚠️ Impossible d'ouvrir la section, tentative de continuation...")

        time.sleep(2)

        # 2. Ouvrir les lignes de fréquence
        open_frequency_lines(driver, len(NOUVELLES_FREQUENCES))
        time.sleep(1)

        # 3. Modifier chaque ligne avec pause avant et après chaque ligne
        total_modified = 0

        for line_index, freq_set in enumerate(NOUVELLES_FREQUENCES):
            print(f"\n{'=' * 60}")
            print(f"📝 LIGNE {line_index + 1}/{len(NOUVELLES_FREQUENCES)}")
            print(f"{'=' * 60}")
            print(f"    Émission: {freq_set['freq_emission_min']} - {freq_set['freq_emission_max']} MHz")
            print(f"    Réception: {freq_set['freq_reception_min']} - {freq_set['freq_reception_max']} MHz")
            print(f"    Puissance: {freq_set['puissance']} {freq_set['unite_puissance']}")

            # Pause AVANT de commencer à modifier cette ligne
            if line_index == 0:
                print("\n🎯 PREMIÈRE LIGNE - PRÊT À COMMENCER")
                print("=" * 50)
                print("📝 INSTRUCTIONS:")
                print("1. Assurez-vous que la section 'Technologie radio' est bien ouverte")

                input("Appuyez sur Entrée pour commencer la PREMIÈRE ligne...")
                print("✓ Début de la première ligne...")
                time.sleep(2)
            else:
                wait_before_line(line_index + 1, len(NOUVELLES_FREQUENCES))

            # Essayer plusieurs méthodes pour chaque champ de fréquence
            field_types = [
                {"key": "freq_emission_min", "patterns": ["emision_min", "emission_min", "freq_min", "emin"]},
                {"key": "freq_emission_max", "patterns": ["emision_max", "emission_max", "freq_max", "emax"]},
                {"key": "freq_reception_min", "patterns": ["recepcion_min", "reception_min", "rec_min", "rmin"]},
                {"key": "freq_reception_max", "patterns": ["recepcion_max", "reception_max", "rec_max", "rmax"]}
            ]

            line_modified = 0

            # Modifier les champs de fréquence
            for field_type in field_types:
                key = field_type["key"]
                patterns = field_type["patterns"]
                new_value = freq_set[key]

                # Essayer plusieurs méthodes pour trouver et modifier le champ
                modified = False

                # Méthode 1: Par nom exact avec préfixe "tr_banda_"
                for pattern in patterns:
                    field_name = f"tr_banda_freq_{pattern}"
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR,
                                                        f"[name='{field_name}'], [data-name='{field_name}']")

                        # Si plusieurs éléments, prendre celui correspondant à la ligne
                        if elements:
                            if line_index < len(elements):
                                elem = elements[line_index]
                            else:
                                elem = elements[0]  # Prendre le premier si pas assez d'éléments

                            if elem.is_displayed():
                                elem.click()
                                elem.clear()
                                elem.send_keys(new_value)
                                print(f"    ✓ {field_name}: {new_value}")
                                total_modified += 1
                                line_modified += 1
                                modified = True
                                time.sleep(0.5)
                                break
                    except:
                        continue

                # Méthode 2: Par nom partiel
                if not modified:
                    for pattern in patterns:
                        try:
                            # Chercher par nom contenant le pattern
                            elements = driver.find_elements(By.CSS_SELECTOR,
                                                            f"[name*='{pattern}'], [data-name*='{pattern}']")

                            if elements:
                                if line_index < len(elements):
                                    elem = elements[line_index]
                                else:
                                    elem = elements[0]

                                if elem.is_displayed():
                                    elem.click()
                                    elem.clear()
                                    elem.send_keys(new_value)
                                    print(f"    ✓ {pattern}: {new_value}")
                                    total_modified += 1
                                    line_modified += 1
                                    modified = True
                                    time.sleep(0.5)
                                    break
                        except:
                            continue

                # Méthode 3: JavaScript pour trouver et modifier
                if not modified:
                    js_modify = """
                    var lineIndex = arguments[0];
                    var fieldPatterns = arguments[1];
                    var newValue = arguments[2];

                    // Chercher tous les champs
                    var fields = document.querySelectorAll('input, span, div[contenteditable="true"]');
                    var fieldFound = null;

                    for(var field of fields) {
                        var name = field.getAttribute('name') || field.getAttribute('data-name') || '';
                        var id = field.id || '';
                        var placeholder = field.getAttribute('placeholder') || '';

                        // Vérifier si le champ correspond aux patterns
                        for(var pattern of fieldPatterns) {
                            if(name.toLowerCase().includes(pattern.toLowerCase()) || 
                               id.toLowerCase().includes(pattern.toLowerCase()) ||
                               placeholder.toLowerCase().includes(pattern.toLowerCase())) {
                                fieldFound = field;
                                break;
                            }
                        }

                        if(fieldFound) break;
                    }

                    if(fieldFound) {
                        // Modifier le champ
                        if(fieldFound.tagName.toLowerCase() === 'input') {
                            fieldFound.value = newValue;
                        } else {
                            fieldFound.textContent = newValue;
                        }

                        // Déclencher les événements
                        fieldFound.dispatchEvent(new Event('input', { bubbles: true }));
                        fieldFound.dispatchEvent(new Event('change', { bubbles: true }));
                        fieldFound.dispatchEvent(new Event('blur', { bubbles: true }));

                        return true;
                    }

                    return false;
                    """

                    try:
                        result = driver.execute_script(js_modify, line_index, patterns, new_value)
                        if result:
                            print(f"    ✓ {key} via JS: {new_value}")
                            total_modified += 1
                            line_modified += 1
                            modified = True
                    except:
                        pass

            # Modifier le champ de puissance
            power_modified = modify_power_field(driver, line_index, freq_set['puissance'], freq_set['unite_puissance'])
            if power_modified:
                line_modified += 1
                total_modified += 1

            # Résumé de la ligne
            if line_modified > 0:
                print(f"\n    ✅ Ligne {line_index + 1}: {line_modified}/5 champs modifiés")
                print(f"      - Fréquences: {freq_set['freq_emission_min']}-{freq_set['freq_emission_max']}/{freq_set['freq_reception_min']}-{freq_set['freq_reception_max']} MHz")
                print(f"      - Puissance: {freq_set['puissance']} {freq_set['unite_puissance']}")

                # Prendre une capture d'écran de cette ligne

                # Pause interactive pour sauvegarde manuelle (sauf pour la dernière ligne)
                if line_index < len(NOUVELLES_FREQUENCES) - 1:
                    wait_for_manual_save(line_index + 1, len(NOUVELLES_FREQUENCES))

                    # Ré-ouvrir la section pour la ligne suivante
                    print("\n🔄 Préparation de la ligne suivante...")
                    time.sleep(2)

                    # Ré-ouvrir la ligne suivante
                    try:
                        lines = driver.find_elements(By.XPATH, "//tr[contains(@class, 'o_data_row')]")
                        if line_index + 1 < len(lines):
                            lines[line_index + 1].click()
                            print(f"✓ Ligne {line_index + 2} ouverte pour modification")
                            time.sleep(1)
                    except:
                        pass
            else:
                print(f"\n    ⚠️ Ligne {line_index + 1}: Aucun champ modifié")

                # Continuer quand même
                if line_index < len(NOUVELLES_FREQUENCES) - 1:
                    wait_for_manual_save(line_index + 1, len(NOUVELLES_FREQUENCES))

            # Petite pause entre les lignes
            time.sleep(1)

        if total_modified > 0:
            print(f"\n{'=' * 60}")
            print(f"📊 RÉCAPITULATIF FINAL")
            print(f"{'=' * 60}")
            print(f"✓ Total: {total_modified} champ(s) modifié(s)")
            print(f"✓ {len(NOUVELLES_FREQUENCES)} ligne(s) traitée(s)")

            # Dernière pause pour sauvegarde finale
            print(f"\n{'=' * 60}")
            print("🎯 DERNIÈRE ÉTAPE")
            print(f"{'=' * 60}")
            print("1. Vérifiez toutes les modifications (fréquences et puissances)")
            print("2. Cliquez sur 'Sauvegarder' pour enregistrer la dernière ligne")
            print("3. Revenez à ce script et appuyez sur Entrée")
            print(f"{'=' * 60}")

            input("Appuyez sur Entrée après la sauvegarde finale...")

            return True
        else:
            print("⚠️ Aucun champ modifié sur aucune ligne")

            # Afficher les champs disponibles pour débogage
            print("\n🔍 Champs disponibles (débogage)...")
            try:
                fields_js = """
                var fields = [];
                var allElements = document.querySelectorAll('input, span, div, label');

                for(var elem of allElements) {
                    var name = elem.getAttribute('name') || elem.getAttribute('data-name') || '';
                    var id = elem.id || '';
                    var text = elem.textContent || elem.value || elem.placeholder || '';

                    if(text.includes('MHz') || text.includes('freq') || name.includes('freq') || 
                       name.includes('banda') || id.includes('freq') || id.includes('banda') ||
                       text.includes('W') || name.includes('potencia') || id.includes('potencia')) {
                        fields.push({
                            tag: elem.tagName,
                            name: name,
                            id: id,
                            value: elem.value || elem.textContent,
                            placeholder: elem.placeholder || '',
                            className: elem.className
                        });
                    }
                }
                return fields;
                """

                fields = driver.execute_script(fields_js)
                for i, field in enumerate(fields[:20]):  # Limiter à 20 pour éviter trop d'output
                    print(
                        f"  Champ {i + 1}: {field['tag']} - name:{field['name']}, id:{field['id']}, value:{field['value']}")

                if len(fields) > 20:
                    print(f"  ... et {len(fields) - 20} autres champs")

            except Exception as e:
                print(f"  Erreur débogage: {e}")

            return False

    except Exception as e:
        print(f"❌ Erreur modification fréquences: {e}")
        import traceback
        traceback.print_exc()
        return False


def main_workflow(driver):
    """Workflow principal pour modifier les fréquences avec pauses"""
    print("=" * 60)
    print("MODIFICATION DES FRÉQUENCES RADIO - MODE INTERACTIF")
    print(f"Configuration de {len(NOUVELLES_FREQUENCES)} ligne(s) de fréquences:")
    print("=" * 60)


    band_names = [
        "WiFi 2.4 GHz", "Bluetooth", "WiFi 5 GHz", "WiFi 6E", "RFID",
        "GSM 900", "GSM 1800", "LTE 800", "LTE 1800", "LTE 2600", "UMTS 900", "UMTS 2100"
    ]

    for i, freq_set in enumerate(NOUVELLES_FREQUENCES):
        # Formater les fréquences
        if freq_set['freq_emission_min'] == freq_set['freq_emission_max']:
            emission = f"{freq_set['freq_emission_min']}"
        else:
            emission = f"{freq_set['freq_emission_min']}-{freq_set['freq_emission_max']}"

        if freq_set['freq_reception_min'] == freq_set['freq_reception_max']:
            reception = f"{freq_set['freq_reception_min']}"
        else:
            reception = f"{freq_set['freq_reception_min']}-{freq_set['freq_reception_max']}"

        band_type = band_names[i] if i < len(band_names) else f"Ligne {i+1}"
        puissance = f"{freq_set['puissance']} {freq_set['unite_puissance']}"

        print(f"│ {i + 1:4d} │ {emission:31} │ {reception:31} │ {band_type:12} │ {puissance:11} │")


    print("=" * 60)

    # Demander confirmation
    input("Appuyez sur Entrée pour commencer...")

    # 1. Activer le mode édition
    if not find_and_click_edit_button(driver):
        print("❌ Impossible d'activer le mode édition")
        return False

    # 2. Modifier les champs de fréquence avec pauses
    if not modify_frequency_fields_with_pauses(driver):
        print("❌ Échec de la modification des fréquences")
        return False

    # 3. Prendre une capture d'écran finale
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"frequences_modifiees_final_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"\n📸 Capture d'écran finale sauvegardée: {filename}")

    return True

# -------------------------
# MAIN
# -------------------------
def main():

    print("=" * 60)

    driver = setup_browser()

    try:
        # Connexion
        if not login_to_odoo(driver):
            print("❌ Connexion échouée")
            return

        # Navigation
        if not navigate_to_demand(driver):
            print("❌ Navigation échouée")
            return

        # Exécution du workflow principal
        success = main_workflow(driver)

        if success:
            print("\n" + "=" * 60)
            print("🎉 MODIFICATION DES FRÉQUENCES ET PUISSANCES TERMINÉE AVEC SUCCÈS!")
            print("=" * 60)
            print("📋 RÉCAPITULATIF COMPLET (12 lignes):")
            for i, freq_set in enumerate(NOUVELLES_FREQUENCES):
                band_name = band_names[i] if i < len(band_names) else f"Ligne {i+1}"
                print(f"  {band_name}:")
                print(f"    Émission: {freq_set['freq_emission_min']}-{freq_set['freq_emission_max']} MHz")
                print(f"    Réception: {freq_set['freq_reception_min']}-{freq_set['freq_reception_max']} MHz")
                print(f"    Puissance: {freq_set['puissance']} {freq_set['unite_puissance']}")
                if i < len(NOUVELLES_FREQUENCES) - 1:
                    print(f"    {'─' * 50}")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ LA MODIFICATION A RENCONTRÉ DES PROBLÈMES")
            print("Vérifiez manuellement les modifications.")
            print("=" * 60)

        # Pause pour vérification manuelle
        print("\n⏳ Fermeture dans 30 secondes...")
        time.sleep(30)

    except KeyboardInterrupt:
        print("\n⚠️ Interruption manuelle détectée")
        time.sleep(5)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(10)
    finally:
        driver.quit()
        print("✅ Navigateur fermé")


if __name__ == "__main__":
    main()