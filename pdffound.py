import os
import PyPDF2


chemin_dossier = r"F:\ATTESTATIONS SALARIES DECLARES"
mot_cle = "MAQROTE ABDELHADI "


for nom_fichier in os.listdir(chemin_dossier):
    if nom_fichier.endswith(".pdf"):
        chemin_pdf = os.path.join(chemin_dossier, nom_fichier)

        try:
            with open(chemin_pdf, 'rb') as fichier:
                lecteur_pdf = PyPDF2.PdfReader(fichier)
                contenu = ""
                for page in lecteur_pdf.pages:
                    contenu += page.extract_text()

                if mot_cle.lower() in contenu.lower():
                    print(f"✅ Mot-clé trouvé dans : {nom_fichier}")
        except Exception as e:
            print(f"❌ Erreur avec le fichier {nom_fichier} : {e}")
