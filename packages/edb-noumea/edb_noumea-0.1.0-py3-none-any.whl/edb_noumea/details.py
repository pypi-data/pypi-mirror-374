import pandas as pd
import tabula
import requests
import io

# URL du fichier PDF contenant les résultats détaillés
PDF_URL = "https://www.noumea.nc/sites/default/files/noumea-pratique-salubrite-publique-resultats/2025/250905-resultats-surveillance-ebm.pdf"

def get_detailed_results():
    """
    Télécharge le PDF des résultats détaillés, en extrait le premier tableau
    et le retourne sous forme de DataFrame pandas.
    """
    print(f"📥 Téléchargement du PDF depuis {PDF_URL}...")
    try:
        # Effectuer la requête HTTP pour obtenir le contenu du PDF
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(PDF_URL, headers=headers)
        response.raise_for_status()
        print("✅ Téléchargement terminé.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du téléchargement du fichier PDF : {e}")
        return None

    # Utiliser un buffer en mémoire pour éviter de sauvegarder le fichier sur le disque
    pdf_file = io.BytesIO(response.content)

    try:
        print("🔍 Extraction des tableaux du PDF...")
        # Extraire tous les tableaux de la première page du PDF
        # L'option pages='1' est importante pour ne pas scanner tout le document
        tables = tabula.read_pdf(pdf_file, pages='1', stream=True)
    except Exception as e:
        print(f"❌ Une erreur est survenue lors de l'extraction des données du PDF.")
        print("ℹ️  Cela peut être dû à l'absence de Java sur votre système, qui est requis par la bibliothèque 'tabula-py'.")
        print(f"   Erreur originale : {e}")
        return None


    if not tables:
        print("❌ Aucun tableau n'a été trouvé dans le PDF.")
        return None

    print(f"✅ {len(tables)} tableau(x) trouvé(s). Affichage du premier.")
    
    # Le premier tableau est notre cible
    df = tables[0]

    # --- Nettoyage du DataFrame ---
    
    # 1. Définir les noms de colonnes attendus en snake_case.
    columns_to_keep = {
        df.columns[0]: "site",
        df.columns[1]: "point_de_prelevement",
        df.columns[2]: "date",
        df.columns[4]: "heure",
        df.columns[6]: "e_coli_npp_100ml",
        df.columns[9]: "enterocoques_npp_100ml"
    }

    # 2. Sélectionner uniquement ces colonnes et en faire une copie
    cleaned_df = df[columns_to_keep.keys()].copy()

    # 3. Renommer les colonnes
    cleaned_df.rename(columns=columns_to_keep, inplace=True)

    # 4. Remplacer les valeurs non numériques et convertir en type numérique
    cleaned_df.replace({'<10': 0}, inplace=True)
    
    # Convertir les colonnes en numérique, les erreurs deviendront NaN (non-numérique)
    cleaned_df['e_coli_npp_100ml'] = pd.to_numeric(cleaned_df['e_coli_npp_100ml'], errors='coerce')
    cleaned_df['enterocoques_npp_100ml'] = pd.to_numeric(cleaned_df['enterocoques_npp_100ml'], errors='coerce')

    # Remplir les éventuelles valeurs NaN qui auraient pu être créées
    cleaned_df.fillna(0, inplace=True)

    return cleaned_df

if __name__ == "__main__":
    # Obtenir le DataFrame des résultats détaillés
    detailed_df = get_detailed_results()

    # Afficher le DataFrame s'il a été créé avec succès
    if detailed_df is not None:
        print("\n📋 Voici les détails des derniers relevés :")
        print(detailed_df.to_string())
