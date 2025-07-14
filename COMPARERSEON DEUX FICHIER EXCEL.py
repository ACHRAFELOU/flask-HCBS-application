import pandas as pd

# Chemins des fichiers Excel
chemin_excel_mouwafaqua = 'C:/Users/a.elouerghi/Desktop/Factures non parvenues/Factures mouwafaqua.xlsx'
chemin_excel_sag = 'C:/Users/a.elouerghi/Desktop/Factures non parvenues/FACTURES SAG NP AU 26-12-2023.xlsx'

# Charger les fichiers Excel dans des DataFrames
df_mouwafaqua = pd.read_excel(chemin_excel_mouwafaqua)
df_sag = pd.read_excel(chemin_excel_sag)

# Vérifier si les valeurs de la colonne "N° facture" du fichier "Factures mouwafaqua.xlsx"
# sont présentes dans la colonne "Numéro de la facture" du fichier "FACTURES SAG NP AU 26-12-2023.xlsx"
df_sag['Commentaire DTEC (SAG)'] = df_sag.apply(lambda x: 'N° SAUTEE' if x['Numéro de la facture'] not in df_mouwafaqua['N° facture'].values else x['Commentaire DTEC (SAG)'], axis=1)

# Enregistrer les modifications dans le fichier "FACTURES SAG NP AU 26-12-2023.xlsx"
df_sag.to_excel(chemin_excel_sag, index=False)
