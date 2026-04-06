import discord
from discord.ext import tasks, commands
from playwright.async_api import async_playwright 
from bs4 import BeautifulSoup
import asyncio
import datetime

# Config
TOKEN = 'TON_TOKEN_DISCORD' 
CHANNEL_ID = 1479948151849881721 # TON_ID_SALON

# -Fonctions scrapping async-
async def get_amazon_prices():
    # On utilise "async with" au lieu de "with"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        urls = {
             "France 🇫🇷": "https://www.amazon.fr/Playstation-%C3%89dition-Num%C3%A9rique-Manette-DualSense/dp/B0FN7ZG39D/",
            "Espagne 🇪🇸": "https://www.amazon.es/Playstation-%C3%89dition-Num%C3%A9rique-Manette-DualSense/dp/B0FN7ZG39D/",
            "Allemagne 🇩🇪": "https://www.amazon.de/Playstation-%C3%89dition-Num%C3%A9rique-Manette-DualSense/dp/B0FN7ZG39D/"
        }
        results = {}

        for country, url in urls.items():
            try:
                # On ajoute "await" devant chaque action de page
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(2) # On utilise asyncio.sleep au lieu de time.sleep
                
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                price_element = soup.find("span", {"class": "a-price-whole"})
                
                if price_element:
                    price = price_element.get_text(strip=True).replace('\u202f', '').replace(',', '')
                    results[country] = f"**{price}€**"
                else:
                    results[country] = "Non trouvé"
            except:
                results[country] = "Erreur"
        
        await browser.close()
        return results

# Code bot
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # Pour corriger les WARNING sur les intents
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.daily_report.start()

    async def on_ready(self):
        print(f'Connecté en tant que {self.user.name}')

    @tasks.loop(minutes=2)
    async def daily_report(self):
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            print(f"Lancement du check de {datetime.datetime.now().strftime('%H:%M:%S')}")
           
            prices = await get_amazon_prices()
            
            embed = discord.Embed(title="📊 Prix PS5", color=discord.Color.green())
            for country, price in prices.items():
                embed.add_field(name=country, value=price, inline=True)
            
            await channel.send(embed=embed)

bot = MyBot()
bot.run(TOKEN)