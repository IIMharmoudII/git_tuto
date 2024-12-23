# -*- coding: utf-8 -*-

import discord
from discord.ext import tasks
from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')  # Assure-toi que le TOKEN est dans ton fichier .env

# Configurer les intents
intents = discord.Intents.default()
intents.messages = True  # Permet de gérer les messages
intents.message_content = True  # Accès au contenu des messages
intents.guilds = True  # Permet de gérer les guildes

# Initialisation du bot
bot = discord.Client(intents=intents)

# === Smash or Pass ===
TARGET_CHANNEL_ID = 1312570416665071797  # ID du canal Smash or Pass
VALID_REACTIONS = ["👍", "👎"]  # Réactions possibles
message_threads = {}  # Stocker les IDs des threads associés aux messages

# === Serveur Web (Flask) ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot Smash or Pass est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Gestion des événements du bot ===

@bot.event
async def on_ready():
    print(f"Bot Smash or Pass connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    """Gestion des messages pour le Smash or Pass."""
    if message.author.bot:
        return  # Ignorer les messages des bots

    # Vérifier si le message est dans le canal ciblé
    if message.channel.id == TARGET_CHANNEL_ID:
        # Supprimer les messages sans pièce jointe
        if not message.attachments:
            await message.delete()
            return

        # Ajouter les réactions spécifiées au message
        for reaction in VALID_REACTIONS:
            await message.add_reaction(reaction)

        # Créer un fil de discussion pour le message
        thread_name = f"Fil de {message.author.display_name}"
        thread = await message.create_thread(name=thread_name)
        message_threads[message.id] = thread.id

        # Envoyer un message d'introduction dans le fil de discussion
        await thread.send(
            f"Bienvenue dans le fil de discussion pour l'image postée par {message.author.mention}.\n"
            f"Merci de respecter la personne et de rester courtois. Tout propos méprisant, dévalorisant, insultant ou méchant est interdit et sera sanctionné !"
        )

    # Toujours traiter les commandes après les autres actions
    await bot.process_commands(message)

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)
