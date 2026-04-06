# 🤖 Bots Discord — Suivi de prix Amazon & Veille Vinted

Deux bots Discord autonomes développés en Python avec une architecture commune basée sur Playwright et discord.py.

Le **bot Amazon** est la base du projet : il scrape le prix d'un produit sur plusieurs marchés européens et l'envoie automatiquement dans un salon Discord.

Le **bot Vinted** en est l'évolution directe : il applique la même logique de scraping asynchrone pour surveiller les nouvelles annonces Vinted selon des critères configurables, avec en plus un système de mémoire anti-doublon et un calcul automatique du coût total.

---

## ✨ Fonctionnalités

### 🛒 Bot Amazon
- Scraping du prix en temps réel sur Amazon FR, ES et DE
- Envoi d'un embed Discord formaté avec les prix par pays et drapeaux
- Rafraîchissement automatique toutes les 2 minutes

### 👕 Bot Vinted
- Surveillance de plusieurs catégories en parallèle (marque + prix max)
- Calcul du coût total estimé : prix article + protection acheteur (0,70€ + 5%) + port (2,88€)
- Extraction automatique de la taille et de l'état de l'article
- Mémoire anti-doublon persistante via fichier `deja_vus.txt`
- Embed Discord par article avec image, prix, taille, état et lien direct
- Auto-installation des dépendances au premier lancement

---

## 🛠️ Stack technique

```
Python        → logique principale
discord.py    → bot et envoi d'embeds
Playwright    → scraping JavaScript (navigateur headless Chromium)
BeautifulSoup → parsing HTML
asyncio       → exécution asynchrone
```

---

## ⚙️ Installation

```bash
pip install discord.py playwright beautifulsoup4
playwright install chromium
```

> Le bot Vinted installe automatiquement les dépendances au premier lancement.

---

## 🚀 Configuration

### Bot Amazon

Modifie ces deux lignes dans `bot_amazon.py` :

```python
TOKEN = 'TON_TOKEN_DISCORD'
CHANNEL_ID = TON_ID_SALON
```

Pour changer le produit surveillé, modifie les URLs dans le dictionnaire `urls` :

```python
urls = {
    "France 🇫🇷": "https://www.amazon.fr/...",
    "Espagne 🇪🇸": "https://www.amazon.es/...",
    "Allemagne 🇩🇪": "https://www.amazon.de/..."
}
```

### Bot Vinted

Ajoute autant de catégories que tu veux dans `CONFIG_VINTED` :

```python
CONFIG_VINTED = [
    {
        "nom": "Ralph Lauren < 15€",
        "url": "https://www.vinted.fr/catalog?search_text=Ralph%20lauren&price_to=15.00&order=newest_first",
        "channel_id": TON_ID_SALON,
        "color": 0x0158a8
    },
    # Ajoute d'autres catégories ici...
]

TOKEN = 'TON_TOKEN_DISCORD'
```

---

## ▶️ Lancement

```bash
# Bot Amazon
python bot_amazon.py

# Bot Vinted
python bot_vinted.py
```

---

## 📌 Notes

- Les deux bots tournent en continu — idéal sur un VPS ou Raspberry Pi pour un usage permanent.
- Le fichier `deja_vus.txt` (bot Vinted) est créé automatiquement et persiste entre les sessions.
- Ne partage jamais ton token Discord publiquement.
