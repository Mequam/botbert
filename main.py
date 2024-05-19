import discord
from discord import app_commands
from discord.ext import commands
import os



from components.antsysub import AntsySubCog
from components.samgob import SamGobCog

#create the bot that we want to work with
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot("/",intents=intents)


@bot.tree.command(name="echo",description="echo a message")
@app_commands.describe(message="the thing to echo")
async def echo(interaction: discord.Interaction, message : str)->None:
    """
    simple echo command to make sure that everything is working properly
    """
    await interaction.response.send_message(message)

@bot.tree.command(name="sync",description="sync the command tree")
async def sync(interaction: discord.Interaction)->None:
    """
    simple echo command to make sure that everything is working properly
    """
    await bot.tree.sync()
    await interaction.response.send_message("request sent, might take discord a sec :)")

@bot.event
async def on_ready():
    import sys

    await bot.add_cog(AntsySubCog(bot))
    await bot.add_cog(SamGobCog(bot))

    print(f'{bot.user} is connected to the following guilds\n')
    for guild in bot.guilds:
        print(
        f'{guild.name}(id: {guild.id})'
    )
    if len(sys.argv) > 1 and sys.argv[1] == '-s':
        print('[on_ready] syncing tree!')
        await bot.tree.sync()
        print('[on_ready] done! discord might take a minute to update')



TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
