
import pandas as pd
import tabula
import requests
import io
from bs4 import BeautifulSoup

# URL de la page officielle contenant le lien vers le PDF
PAGE_URL = "https://www.noumea.nc/noumea-pratique/salubrite-publique/qualite-eaux-baignade"


def get_latest_pdf_url():
    """
    Récupère dynamiquement l'URL du dernier PDF d'analyses détaillées depuis la page officielle.
    """
    print(f"🔗 Recherche du lien PDF sur {PAGE_URL} ...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        resp = requests.get(PAGE_URL, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Impossible de récupérer la page officielle : {e}")
        return None
    soup = BeautifulSoup(resp.text, "lxml")
    # Chercher le premier lien PDF dans la page
    link = soup.find("a", href=lambda h: h and h.endswith(".pdf"))
    if not link:
        print("❌ Aucun lien PDF trouvé sur la page.")
        return None
    pdf_url = link["href"]
    # Si le lien est relatif, le rendre absolu
    if pdf_url.startswith("/"):
        pdf_url = "https://www.noumea.nc" + pdf_url
    print(f"✅ Lien PDF trouvé : {pdf_url}")
    return pdf_url

def get_detailed_results():
    """
    Télécharge dynamiquement le PDF des résultats détaillés, en extrait le premier tableau
    et le retourne sous forme de DataFrame pandas.
    """
    pdf_url = get_latest_pdf_url()
    if not pdf_url:
        return None
    print(f"📥 Téléchargement du PDF depuis {pdf_url} ...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()
        print("✅ Téléchargement terminé.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du téléchargement du fichier PDF : {e}")
        return None

    pdf_file = io.BytesIO(response.content)

    try:
        print("🔍 Extraction des tableaux du PDF...")
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
    df = tables[0]

    # --- Nettoyage du DataFrame ---
    columns_to_keep = {
        df.columns[0]: "site",
        df.columns[1]: "point_de_prelevement",
        df.columns[2]: "date",
        df.columns[4]: "heure",
        df.columns[6]: "e_coli_npp_100ml",
        df.columns[9]: "enterocoques_npp_100ml"
    }
    cleaned_df = df[columns_to_keep.keys()].copy()
    cleaned_df.rename(columns=columns_to_keep, inplace=True)
    cleaned_df.replace({'<10': 0}, inplace=True)
    cleaned_df['e_coli_npp_100ml'] = pd.to_numeric(cleaned_df['e_coli_npp_100ml'], errors='coerce')
    cleaned_df['enterocoques_npp_100ml'] = pd.to_numeric(cleaned_df['enterocoques_npp_100ml'], errors='coerce')
    cleaned_df.fillna(0, inplace=True)

    # Split de la colonne point_de_prelevement
    split_points = cleaned_df['point_de_prelevement'].str.split(',', n=1, expand=True)
    cleaned_df['id_point_prelevement'] = split_points[0].str.strip()
    cleaned_df['desc_point_prelevement'] = split_points[1].str.strip() if split_points.shape[1] > 1 else ''

    # Conversion explicite de la colonne 'date' en type date Python
    cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], format='%d/%m/%Y', errors='coerce').dt.date

    return cleaned_df

if __name__ == "__main__":
    # Obtenir le DataFrame des résultats détaillés
    detailed_df = get_detailed_results()

    # Afficher le DataFrame s'il a été créé avec succès
    if detailed_df is not None:
        print("\n📋 Voici les détails des derniers relevés (toutes colonnes) :")
        print(detailed_df)
        print("\nColonnes du DataFrame :")
        print(list(detailed_df.columns))
