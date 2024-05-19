import samgob
from samgob.iterators.control_flow_iterator import ControlFlowIterator

import discord
from discord import app_commands
from discord.ext import commands



class SamGobCog(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.dice_parser : samgob.DiceSetParser = samgob.DiceSetParser()
        self.bot = bot

    @app_commands.command(name='samgob',description='dice rolling language for text usage')
    @app_commands.describe(query='samon goblin code to execute')
    @app_commands.describe(compile_python='generate python code matching the given query')
    async def samgob(self,inter : discord.Interaction,query : str,compile_python : bool = False)->None:
        
        value = self.dice_parser.compile_langauge(
            ControlFlowIterator(iter(query.split(" ")))
            )

        embeded = discord.Embed(title='samgob query',color=discord.Color.random(),description=query)
        if len(value) > 1000:
            for i in range(0,len(value),1000):
                embeded.add_field(name='roll p.g:' + str(int(i/1000)),value = f'```{value[i:i+1000]}```')
        else:
                embeded.add_field(name='roll',value = f'```{value[0:1000]}```')

        await inter.response.send_message(
                embed=embeded
                )

