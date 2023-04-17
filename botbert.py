import time
import threading
import discord
from discord.ext import commands,tasks 
from collections import deque

class BotBert(commands.Bot):
		def unsubscribe(self,notification,channel):
			#cant unsubscribe if were not subscribed
			if not (notification in self.context_subscriptions):
				return False 
			#is the channel id NOT already in the subscriptions?
			elif not channel.id in [channel.id for channel in self.context_subscriptions[notification]]:
				return False 
			
			#remove channels whos ids mtch the given channel
			self.context_subscriptions = [c for c in self.context_subscriptions[notification] if channel.id != c.id]
			return True 

		#subscribes a notification to the given channel
		def subscribe(self,notification,channel):
				if not (notification in self.context_subscriptions):
					self.context_subscriptions[notification] = [channel]
				elif not channel.id in [channel.id for channel in self.context_subscriptions[notification]]:
					self.context_subscriptions[notification].append(channel)
				else:
					return False 
				
				return True
		#construct the botbert bot
		def __init__(self):
				intents = discord.Intents.default()
				intents.message_content = True

				super().__init__(command_prefix='/botbert ', intents=intents)

				self.capabilities = {}

				#a list of contexts that we are subscribing too
				self.context_subscriptions = {}
			
				self.msg_queue = {}
				

				@self.command()
				async def remember(ctx,arg):
						self.memory = arg
						await ctx.send("[*] saving " + str(arg))

				@self.command()
				async def remind(ctx):
						await ctx.send(self.memory)
				@self.command()
				async def unsubscribe(ctx,notification):
					if self.unsubscribe(notification,ctx.channel):
						await ctx.send(f"unsubscribed to {notification}, sir")
					else:
						await ctx.send(f"sir, you are not subscribed to {notification}")
					
				@self.command()
				async def subscribe(ctx,notification):
					if self.subscribe(notification,ctx.channel):
						await ctx.send(f"subcribed to {notification}, sir")
					else:
						await ctx.send(f"I already subscribed to {notification}, sir")
				@self.command()
				async def listsubs(ctx):
					
					ret_val = "your subscriptions, sir\n" + "-"*10 
					found_notif = False
					for notification in self.context_subscriptions:
						for channel in self.context_subscriptions[notification]:
							if channel.id == ctx.channel.id:
								ret_val += f'\n{notification}'
								found_notif = True
								break 
					if found_notif:
						await ctx.send(ret_val)
					else:
						await ctx.send("sir, you to have no notifications in \"" + str(ctx.channel) + '"')
								
							
				#send over the different capabilities that botbert is subscribed to
				@self.command()
				async def caps(ctx):
						ret_val = "my capabilities, sir, \n"
						for cap in self.capabilities:
								ret_val += cap + " "
								await ctx.send(ret_val[:-1])
				@self.event 
				async def on_ready():
					#start the printer task
					self.send_notif_loop.start()
		
		#async task that sends cached mesages to discord	
		@tasks.loop(seconds=1)
		async def send_notif_loop(self):
			send_data = {}
			for subscription in self.msg_queue:
				if not (subscription in self.context_subscriptions):
					continue
				for channel in self.context_subscriptions[subscription]:
					if not channel in send_data:
						send_data[channel] = ""
					send_data[channel] += self.msg_queue[subscription]
			
			for channel in send_data:
				await channel.send(send_data[channel])
			
			self.msg_queue.clear()
#		@printer.before_loop
#		async def before_printer(self):
#			print("waiting...")
#			#await self.bot.wait_until_ready()
#
		def notify(self,subscription,msg,end="\n"):
			if not (subscription in self.msg_queue):
				self.msg_queue[subscription] = ""
			self.msg_queue[subscription] += msg + end
			
		#start the bot in a seperate thread
		def serve(self):
			t = threading.Thread(target=self.run_token)
			t.start()
		#convinence function to run the bot
		def run_token(self):
			self.run(self.get_token())
		
		#convinence function that attempts to return
		#the token for the bot
		def get_token(path,fpath="./token.txt"):
				f = open(fpath,'r')
				line = f.readline()[:-1]
				f.close()
				return line 
			
		#takes a function that represents a notification
		#that botbert can give us
		def notification(self,wait_time = 10):
				async def decorator(f):
						self.capabilities[f.__name__] = f
						await bb.wait_thread(f,wait_time)
						return f
				return decorator
			
		#	 def run(self,token=None):
		#	 if token == None:
		#	 token = self.get_token()
		#	 super.run(token)
		#
def main():
	bb = BotBert()
	bb.serve()
	while True:
		time.sleep(5)
		bb.notify("test","your test, sir")
if __name__ == '__main__':
	main()
