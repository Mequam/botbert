import discord
from discord import app_commands
from discord.ext import commands,tasks

import requests
from bs4 import BeautifulSoup, NavigableString
import time

#for saving subscriptions
import json


check_time = 10

check_URL = "https://www.antsylabs.com/products/fidget-cube-the-original-fidget-toy"
class AntsySubCog(commands.Cog):
    antsysub = app_commands.Group(name='subscribe',description='ask to recive continual data in this channel')

    def __init__(self,bot : commands.Bot,datafile : str = 'subscriptions.json')->None:
        self.datafile = datafile
        self.bot = bot
        self.notify_threads.start()

    @antsysub.command(name='quickcheck',description='do a quick check at the provided url')
    @app_commands.describe(url='the link to check if items are in stock')
    @app_commands.describe(filt='the filter for grabing html off of the page')
    async def quickcheck(self,inter : discord.Interaction,url : str, filt : str = 'option' )->None:
        await inter.response.send_message(
                        AntsySubCog.get_stock_string(
                            AntsySubCog.check_url(url,filt)
                            )
                        )

    def get_subscription_dict(self)->dict:
        """
        simple function that gets the data representation of the database
        """
        with open(self.datafile,'r') as f:
            return json.load(f)
    
    def store_subscription_dict(self,sub_dict : dict)->None:
        """
        simple function to store the database back into the dictionary
        """
        with open(self.datafile,'w') as f:
            return json.dump(sub_dict,f)

    @antsysub.command(name='sub',description='request continual updates to the given query in this channel')
    @app_commands.describe(url='the link to check if items are in stock')
    @app_commands.describe(filt='the filter for grabing html off of the page')
    async def sub(self,inter : discord.Interaction,url : str, filt : str = 'option'):
        
        subscriptions = self.get_subscription_dict()

        if not inter.guild_id in subscriptions:
            subscriptions[inter.guild_id] = []

        subscriptions[inter.guild_id].append(
                    {'channel_id':inter.channel_id,'author':inter.user.id,'options':[url,filt]}
                )

        self.store_subscription_dict(subscriptions)

        embeded = discord.Embed(title='subscription notification',color=discord.Color.green(),description='added subscript for this channel')
        embeded.add_field(name='url',value=url)
        embeded.add_field(name='filt',value=filt)
        embeded.url = url
        await inter.response.send_message(embed=embeded)

    
    @antsysub.command(name='unsub',description='unsubscribe from continual updates in this channel')
    @app_commands.describe(url='the link to check if items are in stock')
    @app_commands.describe(filt='the filter for grabing html off of the page')
    async def unsub(self,inter : discord.Interaction,url : str, filt : str = 'option'):
        pass

    
    @staticmethod
    def get_stock_string(is_sold_out : dict)->str:
        """
        returns a formated string representing if the given item is in stock or not
        """
        ret_val = "```"
        for key in is_sold_out:
            sold_out = is_sold_out[key]

            ret_val += ("[X] " if sold_out else "[✔] ")+\
                        key+\
                        (" is not sold out!" if not sold_out else " is unfortunately sold out") +\
                        "\n"
        return ret_val + "```"
    
    @tasks.loop(hours=5.0)
    async def notify_threads(self):
        subscriptions = self.get_subscription_dict()
        for guild_id in subscriptions:
            for data in subscriptions[guild_id]:
                channel = self.bot.get_channel(data['channel_id'])

                await channel.send(AntsySubCog.get_stock_string(
                    AntsySubCog.check_url(
                        *data['options']
                        )
                    )
                )



    @staticmethod
    def check_url(check_URL : str,filt : str = 'option')->dict:
        """
        returns a dictionary indicating if any of the given items are in stock or sold out
        """
        check_dict = {}

        check_request = requests.get(check_URL)
        soupy = BeautifulSoup(check_request.text, 'html.parser')

        options = soupy.find_all("select", attrs={"class":"form-options no-js-required"})[0]
        options.find_all(filt)

        for child in options.children:

            # print("\n\n")
            # assert isinstance(child, NavigableString)
            # print(child.title)
            # print(child.parent)
            # print(child.text)
            # print(child)
            # print(str(child))

            string = child.string.strip()
            if string == "": continue
            name = string.split(" ")[0]
            sold_out = (string.find("Sold out")!=-1)
            check_dict[name] = sold_out
        return check_dict
