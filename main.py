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
VALID_REACTIONS = ["👍", "👎"]  # Représente "Validé" et "Pas validé"

# Configurer les intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.dm_messages = True  # Pour envoyer des messages privés

# Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    # Vérifier si le message est dans le bon salon
    if message.channel.id == TARGET_CHANNEL_ID:
        # Supprimer les messages sans image
        if not message.attachments:
            await message.delete()  # Supprime le message sans pièce jointe
            return

        # Ajouter les réactions "Validé" et "Pas validé"
        for reaction in VALID_REACTIONS:
            await message.add_reaction(reaction)

        # Envoyer un message privé à l'utilisateur pour une description
        try:
            await message.author.send(
                f"Bonjour {message.author.mention} ! Vous venez de poster une image dans {message.channel.mention}. "
                f"Souhaitez-vous ajouter une description à votre photo ? Répondez ici pour l'ajouter."
            )
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message privé à {message.author}.")

@bot.event
async def on_reaction_add(reaction, user):
    # Ignorer les réactions du bot
    if user.bot:
        return

    # Vérifier que la réaction est sur un message dans le bon salon
    if reaction.message.channel.id == TARGET_CHANNEL_ID and str(reaction.emoji) in VALID_REACTIONS:
        # Créer un fil avec un nom unique basé sur l'ID du message
        thread_name = f"Fil pour l'image {reaction.message.id}"
        thread = await reaction.message.create_thread(name=thread_name)

        # Ajouter un message dans le fil
        await thread.send(
            f"Bienvenue dans le fil de discussion créé pour l'image postée par {reaction.message.author.mention}. "
            f"Merci de respecter la personne et de rester courtois."
        )

        # Ajouter l'utilisateur au fil
        await thread.add_user(user)

# Lancer le bot
bot.run(TOKEN)
