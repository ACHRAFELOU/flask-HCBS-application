import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Charger les données à partir du fichier Excel
data = pd.read_excel('C:/Users/a.elouerghi/Desktop/Toutes_Factures et reçus_2024/tableau récapitulatif.xlsx')

# Tracer l'histogramme avec une largeur de barre réduite
bars = plt.bar(data['Année'], data['Montant'], width=0.3)  # Ajustez la largeur selon vos préférences

# Formater les étiquettes d'axe x pour afficher les dates en entier
plt.xticks(data['Année'], rotation=45, ha='right')

# Formater les étiquettes d'axe y pour afficher les montants avec des virgules
plt.gca().get_yaxis().set_major_formatter(FuncFormatter(lambda x, _: "{:,.2f}".format(x)))

# Ajouter les montants exacts sur chaque barre
for bar, montant in zip(bars, data['Montant']):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), "{:,.2f}".format(montant),
             ha='center', va='bottom')

# Ajouter des étiquettes et un titre
plt.xlabel('Année')
plt.ylabel('Montant total des factures')
plt.title('Répartition du montant des factures par année')

# Afficher le graphe
plt.show()
