import discord
from discord import app_commands
from discord.ext import commands

import requests
from bs4 import BeautifulSoup, NavigableString
import time


check_time = 10

check_URL = "https://www.antsylabs.com/products/fidget-cube-the-original-fidget-toy"
class AntsySubCog(commands.Cog):
    antsysub = app_commands.Group(name='subscribe',description='ask to recive continual data in this channel')

    def __init__(self,bot : commands.Bot)->None:
        self.bot = bot

    @antsysub.command(name='quickcheck',description='do a quick check at the provided url')
    @app_commands.describe(url='the link to check if items are in stock')
    @app_commands.describe(filt='the filter for grabing html off of the page')
    async def quickcheck(self,inter : discord.Interaction,url : str, filt : str = 'option' )->None:
        await inter.response.send_message(
                        AntsySubCog.get_stock_string(
                            AntsySubCog.check_url(url,filt)
                            )
                        )

    @antsysub.command(name='sub',description='request continual updates to the given query in this channel')
    @app_commands.describe(url='the link to check if items are in stock')
    @app_commands.describe(filt='the filter for grabing html off of the page')
    async def sub(self,inter : discord.Interaction,url : str, filt : str = 'option'):
        pass

    
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
        ret_val = ""
        for key in is_sold_out:
            sold_out = is_sold_out[key]

            ret_val += ("[X] " if sold_out else "[✔] ")+\
                        key+\
                        (" is not sold out!" if not sold_out else " is unfortunately sold out") +\
                        "\n"
        return ret_val


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
