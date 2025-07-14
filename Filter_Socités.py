import pandas as pd
import os  # Importer os pour vérifier si le fichier est bien créé

# Charger le fichier Excel
df = pd.read_excel(r"C:\Users\a.elouerghi\Desktop\Sociétés_actives.xlsx")

# Vérifier les noms des colonnes
print("Colonnes du fichier :", df.columns)

# Compter le nombre d'occurrences de chaque (Nom, Téléphone, Email)
df["Nombre d'occurrences"] = df.groupby(["Nom"])["Nom"].transform("count")

# Supprimer les doublons en gardant une seule occurrence
df_unique = df.drop_duplicates(subset=["Nom"])

# Sauvegarder le fichier mis à jour
output_path = r"C:\Users\a.elouerghi\Documents\Sociétés_actives_sans_doublons.xlsx"
df_unique.to_excel(output_path, index=False, engine="openpyxl")

# Vérifier si le fichier a bien été enregistré
if os.path.exists(output_path):
    print(f"✅ Traitement terminé. Le fichier mis à jour est enregistré sous : {output_path}")
else:
    print("❌ Erreur : Le fichier ne s'est pas enregistré.")
