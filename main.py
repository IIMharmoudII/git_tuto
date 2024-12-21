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

# Stocker les descriptions déjà ajoutées pour éviter les mises à jour multiples
user_descriptions = {}

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
            if message.author.id not in user_descriptions:
                await message.author.send(
                    f"Bonjour {message.author.mention} ! Vous venez de poster une image dans {message.channel.mention}. "
                    f"Souhaitez-vous ajouter une description à votre photo ? Répondez ici pour l'ajouter. "
                    f"(Votre description sera ajoutée au fil dédié à votre photo)."
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
        # Créer un fil avec un nom unique basé sur l'auteur
        thread_name = f"Fil de {reaction.message.author.display_name}"
        thread = await reaction.message.create_thread(name=thread_name)

        # Ajouter un message dans le fil
        await thread.send(
            f"Bienvenue dans le fil de discussion créé pour l'image postée par {reaction.message.author.mention}. "
            f"Merci de respecter la personne et de rester courtois."
        )

        # Ajouter une description si elle existe
        if reaction.message.author.id in user_descriptions:
            description = user_descriptions[reaction.message.author.id]
            await thread.send(f"Description ajoutée par l'utilisateur : {description}")

        # Ajouter l'utilisateur au fil
        await thread.add_user(user)

@bot.event
async def on_message_edit(message_before, message_after):
    # Ignorer les messages qui ne sont pas des réponses en DM
    if not message_after.guild and message_after.author.id not in user_descriptions:
        # Enregistrer la description pour l'utilisateur
        user_descriptions[message_after.author.id] = message_after.content
        await message_after.channel.send("Merci ! Votre description a été enregistrée.")
