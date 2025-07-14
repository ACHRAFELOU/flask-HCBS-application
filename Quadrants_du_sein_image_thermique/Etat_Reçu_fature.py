import pandas as pd
import os

# Chemin vers le fichier Excel
chemin_excel = 'C:/Users/a.elouerghi/Desktop/Etat/anrt_facture.xlsx'

# Charger le fichier Excel dans une structure de données
donnees_excel = pd.read_excel(chemin_excel)

# Dossier contenant tes fichiers PDF
dossier_pdf = 'C:/Users/a.elouerghi/Desktop/Etat/Récépissés du 20 au 26 novembre 2023/'

# Parcourir chaque ligne du fichier Excel
for index, row in donnees_excel.iterrows():
    # Récupérer le nom du fichier PDF à partir de la colonne 'Facture'
    nom_fichier_pdf = str(row['N° facture']) + '.pdf'

    # Vérifier si le fichier PDF existe dans le dossier
    if os.path.exists(os.path.join(dossier_pdf, nom_fichier_pdf)):
        # Si le fichier PDF existe, mettre 'Oui' dans la colonne 'Reçu'
        donnees_excel.at[index, 'Reçu/ID'] = 'Oui'

# Enregistrer les modifications dans le fichier Excel
donnees_excel.to_excel(chemin_excel, index=False)
