# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
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
intents.dm_messages = True  # Pour gérer les messages privés

# Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Stocker les descriptions et les fils créés
descriptions = {}
threads_created = {}

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    # Vérifier si le message est dans le bon salon
    if message.channel.id == TARGET_CHANNEL_ID:
        # Supprimer les messages sans image
        if not message.attachments:
            await message.delete()
            return

        # Ajouter les réactions "Validé" et "Pas validé"
        for reaction in VALID_REACTIONS:
            await message.add_reaction(reaction)

        # Créer un fil unique pour l'image
        if message.id not in threads_created:
            thread_name = f"Fil de {message.author.display_name}"
            thread = await message.create_thread(name=thread_name)
            threads_created[message.id] = thread.id

            # Ajouter un message de courtoisie dans le fil
            await thread.send(
                f"Bienvenue dans le fil pour l'image postée par {message.author.mention}. Merci de respecter la personne et de rester courtois."
            )

            # Ajouter l'image dans le fil
            await thread.send(content=f"Image postée par {message.author.mention} :", file=await message.attachments[0].to_file())


@bot.event
async def on_reaction_add(reaction, user):
    # Ignorer les réactions du bot
    if user.bot:
        return

    # Vérifier que la réaction est sur un message dans le bon salon
    if reaction.message.channel.id == TARGET_CHANNEL_ID and str(reaction.emoji) in VALID_REACTIONS:
        if reaction.message.id not in threads_created:
            thread_name = f"Fil de {reaction.message.author.display_name}"
            thread = await reaction.message.create_thread(name=thread_name)
            threads_created[reaction.message.id] = thread.id

            # Ajouter un message dans le fil
            await thread.send(
                f"Bienvenue dans le fil pour l'image postée par {reaction.message.author.mention}. Merci de respecter la personne et de rester courtois."
            )

# Lancer le bot
bot.run(TOKEN)
