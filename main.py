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

# Stockage des fils et descriptions
user_threads = {}
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
            await message.delete()
            return

        # Ajouter les réactions "Validé" et "Pas validé"
        for reaction in VALID_REACTIONS:
            await message.add_reaction(reaction)

        # Créer un fil pour l'image
        thread_name = f"Fil de {message.author.display_name}"
        thread = await message.create_thread(name=thread_name)

        # Envoyer un message dans le fil
        await thread.send(
            f"Bienvenue dans le fil de discussion créé pour l'image postée par {message.author.mention}.\n"
            f"Merci de respecter la personne et de rester courtois."
        )

        # Enregistrer le fil pour l'utilisateur
        user_threads[message.id] = thread.id

        # Envoyer un DM à l'utilisateur pour ajouter une description
        try:
            await message.author.send(
                f"Bonjour {message.author.mention} ! Vous venez de poster une image dans {message.channel.mention}.\n"
                f"Souhaitez-vous ajouter une description à votre photo ? Répondez ici pour l'ajouter."
            )
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message privé à {message.author}.")

@bot.event
async def on_reaction_add(reaction, user):
    # Ignorer les réactions du bot
    if user.bot:
        return

    # Vérifier que la réaction est dans le bon salon et valide
    if reaction.message.channel.id == TARGET_CHANNEL_ID and str(reaction.emoji) in VALID_REACTIONS:
        message_id = reaction.message.id

        # Récupérer le fil existant ou créer un nouveau
        if message_id in user_threads:
            thread = discord.utils.get(reaction.message.channel.threads, id=user_threads[message_id])
        else:
            thread_name = f"Fil de {reaction.message.author.display_name}"
            thread = await reaction.message.create_thread(name=thread_name)
            user_threads[message_id] = thread.id

        # Ajouter un message de respect si le fil est nouveau
        if thread:
            await thread.send(
                f"{user.mention} a ajouté une réaction. Merci de respecter l'auteur de l'image."
            )

@bot.event
async def on_message_delete(message):
    # Supprimer le fil associé à un message supprimé
    if message.id in user_threads:
        thread_id = user_threads.pop(message.id, None)
        if thread_id:
            thread = discord.utils.get(message.channel.threads, id=thread_id)
            if thread:
                await thread.delete()

@bot.event
async def on_message(message):
    # Vérifier les messages privés pour les descriptions
    if not message.guild:
        user_id = message.author.id
        if user_id not in user_descriptions:
            user_descriptions[user_id] = message.content
            await message.channel.send("C'est bon, votre description vient d'être ajoutée.")

            # Ajouter la description au fil associé
            for msg_id, thread_id in user_threads.items():
                if message.author.id == bot.get_message(msg_id).author.id:
                    thread = discord.utils.get(bot.get_channel(TARGET_CHANNEL_ID).threads, id=thread_id)
                    if thread:
                        await thread.send(f"Description ajoutée : {message.content}")
                    break

bot.run(TOKEN)
