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
intents.reactions = True

# Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Stocker les threads créés pour éviter les doublons
message_threads = {}

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

        # Créer un fil pour le message si ce n'est pas déjà fait
        thread_name = f"Fil de {message.author.display_name}"
        if message.id not in message_threads:
            thread = await message.create_thread(name=thread_name)
            message_threads[message.id] = thread.id

            # Message de bienvenue dans le fil
            await thread.send(
                f"Bienvenue dans le fil de discussion pour l'image postée par {message.author.mention}. \n"
                f"Merci de respecter la personne et de rester courtois."
            )

            # Message privé dans le fil visible uniquement par l'auteur
            await thread.send(
                content=f"Vous pouvez envoyer votre description ou vos envies ici. Ce message est visible uniquement par vous.",
                allowed_mentions=discord.AllowedMentions.none()
            )

@bot.event
async def on_reaction_add(reaction, user):
    # Ignorer les réactions du bot
    if user.bot:
        return

    # Vérifier que la réaction est sur un message dans le bon salon
    if reaction.message.channel.id == TARGET_CHANNEL_ID and str(reaction.emoji) in VALID_REACTIONS:
        # Récupérer ou créer le fil associé au message
        if reaction.message.id in message_threads:
            thread_id = message_threads[reaction.message.id]
            thread = await reaction.message.guild.fetch_channel(thread_id)
        else:
            thread_name = f"Fil de {reaction.message.author.display_name}"
            thread = await reaction.message.create_thread(name=thread_name)
            message_threads[reaction.message.id] = thread.id

        # Ajouter un message dans le fil
        await thread.send(
            f"Un utilisateur a réagi à cette image avec {reaction.emoji}. Merci de respecter l'auteur."
        )

# Lancer le bot avec le token
if __name__ == "__main__":
    bot.run(TOKEN)
