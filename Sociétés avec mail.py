import pandas as pd

# Charger le premier fichier (avec les emails)
df1 = pd.read_excel(r"C:\Users\a.elouerghi\Desktop\Sociétés_2025_AE.xlsx")

# Charger le second fichier (sans les emails)
df2 = pd.read_excel(r"C:\Users\a.elouerghi\Desktop\Sociétés_actives_sans_doublons.xlsx")

# Fusionner les deux fichiers sur la colonne "Nom"
df_merged = df2.merge(df1[['Nom', 'Email']], on='Nom', how='left')

# Supprimer les doublons en gardant uniquement les lignes où "Email" n'est pas vide
df_cleaned = df_merged.dropna(subset=['Email'])

# Sauvegarder le fichier mis à jour
output_path = r"C:\Users\a.elouerghi\Desktop\Sociétés_actives_avec_emails.xlsx"
df_cleaned.to_excel(output_path, index=False, engine="openpyxl")

print(f"✅ Traitement terminé. Le fichier mis à jour est enregistré sous : {output_path}")
