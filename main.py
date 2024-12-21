# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')

# ID du salon cible
TARGET_CHANNEL_ID = 1312570416665071797
VALID_REACTIONS = ["👍", "👎"]  # Réactions pour validé/pas validé

# Configurer les intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.reactions = True

# Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents)

# === Serveur Web Flask ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne et répond aux pings !"

# Fonction pour lancer le serveur Flask dans un thread séparé
def run_webserver():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run_webserver)
    thread.start()
    
# Stocker les threads créés pour éviter les doublons
message_threads = {}

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author.bot:
        return

    # Vérifier si le message est dans le bon salon
    if message.channel.id == TARGET_CHANNEL_ID:
        # Supprimer les messages sans image
        if not message.attachments:
            await message.delete()
            return

        # Ajouter les réactions "Validé" et "Pas validé"
        for reaction in VALID_REACTIONS:
            await message.add_reaction(reaction)

        # Créer un fil pour chaque nouvelle image
        thread_name = f"Fil de {message.author.display_name}"
        thread = await message.create_thread(name=thread_name)
        message_threads[message.id] = thread.id

        await thread.send(
            f"Bienvenue dans le fil de discussion pour l'image postée par {message.author.mention}.\n"
            f"Merci de respecter la personne et de rester courtois. Tout propos méprisant, dévalorisant, insultant ou méchant est interdit et sera sanctionné !"
        )

@bot.event
async def on_reaction_add(reaction, user):
    # Ignorer les réactions du bot
    if user.bot:
        return

    # Vérifier que la réaction est sur un message dans le bon salon
    if reaction.message.channel.id == TARGET_CHANNEL_ID and str(reaction.emoji) in VALID_REACTIONS:
        if reaction.message.id in message_threads:
            # Récupérer le thread existant
            thread_id = message_threads[reaction.message.id]
            thread = await reaction.message.guild.fetch_channel(thread_id)
        else:
            # Créer un nouveau thread si besoin (cas improbable)
            thread_name = f"Fil de {reaction.message.author.display_name}"
            thread = await reaction.message.create_thread(name=thread_name)
            message_threads[reaction.message.id] = thread.id

        # Ajouter un message dans le fil
        await thread.send(
            f"{user.mention} a réagi à cette image avec {reaction.emoji}."
        )

# Si Render exige un service web, gardez cette partie
from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Garder ou supprimer selon Render
keep_alive()

# Démarrer le bot
bot.run(TOKEN)
