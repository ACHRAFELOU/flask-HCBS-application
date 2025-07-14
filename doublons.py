import pandas as pd

# Charger le fichier Excel (corriger le chemin si nécessaire)
fichier_source = r"C:\Users\a.elouerghi\Desktop\Stés_2025.xlsx"
fichier_sortie = r"C:\Users\a.elouerghi\Desktop\Stés_2025_sans_doublons.xlsx"

# Lire le fichier Excel
df = pd.read_excel(fichier_source)

# Supprimer les doublons en gardant la première occurrence
df_cleaned = df.drop_duplicates(subset=["Demandeur"], keep="first")

# Enregistrer le fichier modifié
df_cleaned.to_excel(fichier_sortie, index=False)

print("Les lignes dupliquées ont été supprimées. Le fichier mis à jour est enregistré sous :", fichier_sortie)
