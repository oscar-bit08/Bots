import subprocess
import sys
import os

# FONCTION D'AUTO-INSTALLATION DES MODULES

def check_and_install_modules():
    required = {
        "discord": "discord.py",
        "playwright": "playwright",
        "bs4": "beautifulsoup4"
    }
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"📦 Installation de {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # Installation spécifique des navigateurs Playwright
    try:
        import playwright
        print("🌐 Vérification des navigateurs Playwright...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
        subprocess.run([sys.executable, "-m", "playwright", "install-deps"])
    except Exception as e:
        print(f"Note: {e}")

check_and_install_modules()

import discord
from discord.ext import tasks, commands
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import datetime
import re
import os

# CONFIGURATION DES SALONS
# Nombre de catégories modifiable
CONFIG_VINTED = [
    {
        "nom": "Ralph Lauren < 15€",
        "url": "https://www.vinted.fr/catalog?search_text=Ralph%20lauren&price_to=15.00&order=newest_first",
        "channel_id": 100, # Remplace par l'ID du salon souhaité
        "color": 0x0158a8
    },
    {
        "nom": "Levis < 10€",
        "url": "https://www.vinted.fr/catalog?search_text=Levis&price_to=10.00&order=newest_first",
        "channel_id": 100, 
        "color": 0xed1c24
    },
    {
        "nom": "Carhartt < 13€",
        "url": "https://www.vinted.fr/catalog?search_text=Carhartt&price_to=13.00&order=newest_first",
        "channel_id": 100, 
        "color": 0xff7b00
    },
    
]

TOKEN = 'TON_TOKEN_DISCORD' # Remplace par ton token Discord

# GESTION DE LA MÉMOIRE (FICHIER TXT)
# Mémoire
def charger_cache():
    if os.path.exists("deja_vus.txt"):
        with open("deja_vus.txt", "r") as f:
            return set(f.read().splitlines())
    return set()

def sauvegarder_cache(item_id):
    with open("deja_vus.txt", "a") as f:
        f.write(f"{item_id}\n")

articles_deja_vus = charger_cache()

# Scrapping asynchrone avec Playwright
async def scrape_category(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        page = await context.new_page()
        found_items = []
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(7) # Temps nécessaire pour le rendu JavaScript
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            items = soup.find_all("div", {"data-testid": "grid-item"})

            for item in items:
                link_el = item.find("a", href=True)
                if not link_el: continue
                link = link_el['href'] if link_el['href'].startswith("http") else "https://www.vinted.fr" + link_el['href']
                item_id = link.split('/')[-1].split('-')[0]

                if item_id not in articles_deja_vus:
                    # --- EXTRACTION DU PRIX (MULTI-BALISES) ---
                    # Recherche du prix combiné (incluant les frais de service de base)
                    price_el = item.find(True, {"data-testid": "total-combined-price"})
                    d_base, d_ttc = "Inconnu", "Calcul impossible"
                    
                    if price_el:
                        raw = price_el.get_text(strip=True).replace(',', '.')
                        m = re.search(r"(\d+\.\d+|\d+)", raw)
                        if m:
                            base = float(m.group(1))
                            # Calcul TTC : Prix + Protection (0.70€ + 5%) + Port moyen (2.88€)
                            ttc = base + (0.70 + (base * 0.05)) + 2.88
                            d_base, d_ttc = f"{base:.2f}€", f"{ttc:.2f}€"

                    # --- EXTRACTION TAILLE ET ÉTAT ---
                    # On récupère tous les éléments de texte descriptifs
                    info_elements = item.find_all(["p", "span", "h4"])
                    info_text = [i.get_text(strip=True) for i in info_elements]
                    
                    # Logique de repli si les données sont mal indexées
                    taille = "N/A"
                    etat = "Non précisé"
                    
                    for txt in info_text:
                        if any(size in txt.upper() for size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']):
                            taille = txt
                        if "état" in txt.lower() or "neuf" in txt.lower():
                            etat = txt

                    img_tag = item.find("img")
                    found_items.append({
                        "id": item_id, 
                        "title": img_tag['alt'] if img_tag else "Article",
                        "base_price": d_base, 
                        "total_ttc": d_ttc, 
                        "link": link,
                        "image": img_tag['src'] if img_tag else None,
                        "taille": taille, 
                        "etat": etat
                    })
        except Exception as e: 
            print(f"Erreur lors du scan : {e}")
        await browser.close()
        return found_items

# --- BOT ---
class VintedBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.main_loop.start()

    @tasks.loop(minutes=3)
    async def main_loop(self):
        for cat in CONFIG_VINTED:
            new_items = await scrape_category(cat['url'])
            channel = self.get_channel(cat['channel_id'])
            if channel and new_items:
                for item in new_items:
                    embed = discord.Embed(
                        title=f"👕 {item['title']}", 
                        url=item['link'], 
                        color=cat['color'],
                        timestamp=datetime.datetime.now()
                    )
                    # Mise en évidence de la Taille et de l'État sur la même ligne
                    embed.add_field(name="📏 Taille", value=f"**{item['taille']}**", inline=True)
                    embed.add_field(name="✨ État", value=f"**{item['etat']}**", inline=True)
                    
                    # Section Prix bien distincte
                    embed.add_field(name="🏷️ Prix Article", value=f"**{item['base_price']}**", inline=True)
                    embed.add_field(name="💰 TOTAL ESTIMÉ", value=f"🚀 **{item['total_ttc']}**", inline=True)
                    
                    if item['image']: 
                        embed.set_image(url=item['image'])
                    
                    embed.set_footer(text=f"Alerte : {cat['nom']} • Frais de port estimés à 2,88€")
                    
                    await channel.send(embed=embed)
                    articles_deja_vus.add(item['id'])
                    sauvegarder_cache(item['id'])
            await asyncio.sleep(5) # Sécurité anti-spam

bot = VintedBot()
bot.run(TOKEN)