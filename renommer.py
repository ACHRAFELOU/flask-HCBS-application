import pandas as pd
import shutil

# Lire le fichier Excel contenant les numéros de fichier
data = pd.read_excel('C:/Users/a.elouerghi/Desktop/Etat/MTN/Frais-.xlsx')  # Assurez-vous de spécifier le bon nom de votre fichier Excel

# Récupérer les numéros de fichier de la colonne appropriée (par exemple, la colonne 'Noms_des_colonnes')
numeros = data['N° facture']  # Remplacez 'Noms_des_colonnes' par le nom de votre colonne contenant les numéros

# Chemin d'accès au fichier PDF que vous souhaitez copier
chemin_source_pdf = 'C:/Users/a.elouerghi/Desktop/Etat/MTN/Virement.pdf'  # Remplacez ceci par votre propre chemin d'accès

# Chemin d'accès au dossier où vous souhaitez copier les fichiers PDF
dossier_destination = 'C:/Users/a.elouerghi/Desktop/Etat/MTN/Récépissés Candy/'  # Remplacez ceci par votre propre chemin d'accès

# Copie des fichiers PDF basée sur les numéros de la liste Excel
for numero in numeros:
    nom_fichier_copie = f"{numero}.pdf"  # Nom du fichier de copie
    chemin_destination_pdf = dossier_destination + nom_fichier_copie  # Chemin d'accès du fichier de copie

    # Copier le fichier PDF source vers le dossier de destination avec le nouveau nom
    shutil.copy(chemin_source_pdf, chemin_destination_pdf)
