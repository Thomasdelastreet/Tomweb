import requests
import sqlite3
import time
from bs4 import BeautifulSoup

# Configuration du site à scraper
URL = "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal"  # Remplace par l'URL cible
INTERVALLE = 60  # Temps d'attente entre deux scans (en secondes)

# Initialisation de la base SQLite
conn = sqlite3.connect("articles.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT,
    sous_titre TEXT,
    lien TEXT UNIQUE
)
""")
conn.commit()

def recuperer_articles():
    """Récupère les titres, sous-titres et liens des articles"""
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Vérifie si la requête a réussi
    except requests.RequestException as e:
        print(f"Erreur de connexion : {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    # Adaptation selon la structure du site (exemple générique)
    for article in soup.select("article"):  # Modifier le sélecteur selon le site
        titre = article.select_one("h2").text.strip() if article.select_one("h2") else "Sans titre"
        sous_titre = article.select_one("p").text.strip() if article.select_one("p") else "Sans sous-titre"
        lien = article.select_one("a")["href"] if article.select_one("a") else None
        
        if lien and not lien.startswith("http"):
            lien = URL + lien  # Conversion des liens relatifs en absolus
        
        if lien:
            articles.append((titre, sous_titre, lien))
    
    return articles

def enregistrer_articles(articles):
    """Enregistre les articles dans la base de données en évitant les doublons"""
    for titre, sous_titre, lien in articles:
        try:
            cursor.execute("INSERT INTO articles (titre, sous_titre, lien) VALUES (?, ?, ?)", (titre, sous_titre, lien))
            conn.commit()
            print(f"✅ Nouveau : {titre}")
        except sqlite3.IntegrityError:
            print(f"⚠️ Déjà enregistré : {titre}")

if __name__ == "__main__":
    while True:
        print("\n🔄 Scraping en cours...")
        articles = recuperer_articles()
        if articles:
            enregistrer_articles(articles)
        else:
            print("⚠️ Aucune donnée récupérée.")
        
        print(f"⏳ Attente de {INTERVALLE} secondes...")
        time.sleep(INTERVALLE)
