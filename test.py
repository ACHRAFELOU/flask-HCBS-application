import pandas as pd
import os

# Chemin vers le fichier Excel
chemin_excel = 'C:/Users/a.elouerghi/Desktop/Etat/Et.xlsx'

# Charger le fichier Excel dans une structure de données
donnees_excel = pd.read_excel(chemin_excel)

# Dossier contenant tes fichiers PDF
dossier_pdf = 'C:/Users/a.elouerghi/Desktop/Etat/Récépissés du 20 au 26 novembre 2023/'

# Parcourir chaque ligne du fichier Excel
for index, row in donnees_excel.iterrows():
    # Récupérer le numéro de facture au format '.../2023'
    numero_facture_excel = str(row['Facture'])

    # Générer le nom du fichier PDF correspondant au format '...-2023-Reçu.pdf'
    nom_fichier_pdf = f"{numero_facture_excel.replace('/', '-Reçu.pdf')}"

    # Vérifier si le fichier PDF existe dans le dossier
    if os.path.exists(os.path.join(dossier_pdf, nom_fichier_pdf)):
        # Si le fichier PDF existe, mettre 'Oui' dans la colonne correspondante
        donnees_excel.at[index, numero_facture_excel] = 'Oui'

# Enregistrer les modifications dans le fichier Excel
donnees_excel.to_excel(chemin_excel, index=False)
