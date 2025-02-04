import sqlite3
import requests
from bs4 import BeautifulSoup

# Configuration des bases de données
INPUT_DB_PATH = "C:/Users/Thomas/Documents/code/tomweb/crawleropti.db"  # Base de données d'entrée
OUTPUT_DB_PATH = "C:/Users/Thomas/Documents/code/tomweb/crawleropti_output.db"  # Base de données de sortie

# Connexion à la base de données d'entrée
conn_input = sqlite3.connect(INPUT_DB_PATH)
cursor_input = conn_input.cursor()

# Connexion à la base de données de sortie
conn_output = sqlite3.connect(OUTPUT_DB_PATH)
cursor_output = conn_output.cursor()

# Créer la table 'url' dans la base de données d'entrée si elle n'existe pas
cursor_input.execute('''
CREATE TABLE IF NOT EXISTS url (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE
);
''')

# Créer la table 'page_data' dans la base de données de sortie si elle n'existe pas
cursor_output.execute('''
CREATE TABLE IF NOT EXISTS page_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    subtitle TEXT
);
''')

# Fonction pour récupérer les liens depuis la base de données d'entrée
def get_links_from_db():
    cursor_input.execute("SELECT url FROM url")
    rows = cursor_input.fetchall()
    links = [row[0] for row in rows]
    return links

# Fonction pour extraire le titre et le sous-titre d'une page web
def extract_title_and_subtitle(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraction du titre de la page
        title = soup.title.string if soup.title else "Titre non trouvé"

        # Extraction d'un sous-titre (par exemple, le premier h2)
        subtitle = soup.find('h2').string if soup.find('h2') else "Sous-titre non trouvé"

        return title, subtitle
    except requests.RequestException as e:
        print(f"Erreur pour {url}: {e}")
        return None, None

# Fonction pour sauvegarder le titre et le sous-titre dans la base de données de sortie
def save_title_and_subtitle(url, title, subtitle):
    cursor_output.execute("INSERT OR REPLACE INTO page_data (url, title, subtitle) VALUES (?, ?, ?)", (url, title, subtitle))
    conn_output.commit()

# Fonction principale pour traiter les liens et récupérer les titres et sous-titres
def process_links():
    links = get_links_from_db()
    for url in links:
        print(f"Traitement de l'URL : {url}")
        title, subtitle = extract_title_and_subtitle(url)
        if title and subtitle:
            print(f"Titre : {title}\nSous-titre : {subtitle}")
            save_title_and_subtitle(url, title, subtitle)

# Exécution du script
if __name__ == "__main__":
    process_links()

    # Fermeture des connexions aux bases de données
    conn_input.close()
    conn_output.close()
