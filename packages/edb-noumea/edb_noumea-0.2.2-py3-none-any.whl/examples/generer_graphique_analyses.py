import pandas as pd
import matplotlib.pyplot as plt
from edb_noumea.details import get_detailed_results

# Obtenir les données détaillées
df = get_detailed_results()

if df is not None and not df.empty:
    print("Création du graphique E. coli...")

    # Trier les données par E. coli pour une meilleure lisibilité
    df_sorted_ecoli = df.sort_values(by='e_coli_npp_100ml', ascending=False)

    # Créer le graphique à barres horizontales pour E. coli
    plt.figure(figsize=(12, 8))
    plt.barh(df_sorted_ecoli['point_de_prelevement'], df_sorted_ecoli['e_coli_npp_100ml'], color='skyblue')
    plt.xlabel('E. coli (NPP/100ml)')
    plt.ylabel('Point de prélèvement')
    plt.title("Niveaux d'E. coli par Point de Prélèvement")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('ecoli_levels.png')
    print("Graphique E. coli sauvegardé sous 'ecoli_levels.png'")
    plt.close()

    print("Création du graphique Entérocoques...")
    # Trier les données par Entérocoques
    df_sorted_entero = df.sort_values(by='enterocoques_npp_100ml', ascending=False)

    # Créer le graphique à barres horizontales pour Entérocoques
    plt.figure(figsize=(12, 8))
    plt.barh(df_sorted_entero['point_de_prelevement'], df_sorted_entero['enterocoques_npp_100ml'], color='salmon')
    plt.xlabel('Entérocoques (NPP/100ml)')
    plt.ylabel('Point de prélèvement')
    plt.title("Niveaux d'Entérocoques par Point de Prélèvement")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('entero_levels.png')
    print("Graphique Entérocoques sauvegardé sous 'entero_levels.png'")
    plt.close()
else:
    print("Aucune donnée à afficher.")
