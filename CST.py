import win32com.client


def add_material(design, material_name, properties):
    """
    Ajoute un matériau avec des propriétés spécifiques à la gestion des matériaux du design actif.
    """
    try:
        # Vérifier si MaterialManager est disponible
        material_manager = design.MaterialManager
        if material_manager is None:
            raise Exception("Gestion des matériaux non trouvée.")

        material = material_manager.CreateMaterial(material_name)
        for property_name, property_value in properties.items():
            setattr(material, property_name, property_value)
        print(f"Matériau '{material_name}' ajouté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'ajout du matériau : {e}")


def add_component(design, component_name, component_type, properties):
    """
    Ajoute un composant avec des propriétés spécifiques au design actif.
    """
    try:
        component_manager = design.ComponentManager
        if component_manager is None:
            raise Exception("Gestion des composants non trouvée.")

        component = component_manager.CreateComponent(component_name, component_type)
        if component is None:
            raise Exception(f"Échec de la création du composant '{component_name}'.")

        for property_name, property_value in properties.items():
            setattr(component, property_name, property_value)

        print(f"Composant '{component_name}' ajouté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'ajout du composant : {e}")


def main():
    # Chemin du projet
    project_path = r"C:\Users\a.elouerghi\Desktop\cst\ANTENNA\ANTENNA UWB ARRAY BR_CANCER.cst"

    # Connexion à CST Studio Suite
    cst_app = win32com.client.Dispatch("CSTStudio.application")

    # Ouvrir le projet
    try:
        cst_app.OpenFile(project_path)
        print(f"Le projet {project_path} a été ouvert.")
    except Exception as e:
        print(f"Erreur lors de l'ouverture du projet : {e}")
        return

    # Accéder au design actif
    try:
        design = cst_app.ActiveProject.ActiveDesign
        if design is None:
            raise Exception("Aucun design actif trouvé.")
        print(f"Le design actif est '{design.Name}'.")
    except Exception as e:
        print(f"Erreur lors de la récupération du design actif : {e}")
        return

    # Définir les propriétés des matériaux
    material_properties = {
        "Conductivity": 5.8e7,  # Exemple de propriété
        "Permittivity": 2.2,
        "Permeability": 1.0
    }

    # Ajouter des matériaux
    add_material(design, "Copper", material_properties)
    add_material(design, "FR4", material_properties)

    # Définir les propriétés des composants
    component_properties = {
        "Position": (0, 0, 0),  # Exemple de propriété
        "Size": (0.01, 0.01, 0.001)
    }

    # Ajouter des composants
    add_component(design, "GND", "Rectangle", component_properties)
    add_component(design, "SUBSTRAT", "Rectangle", component_properties)
    add_component(design, "Patch1_1", "Patch", component_properties)
    add_component(design, "Patch1_2", "Patch", component_properties)

    # Répétez l'ajout pour les autres composants comme nécessaire


if __name__ == "__main__":
    main()
