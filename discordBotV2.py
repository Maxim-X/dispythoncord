import discord
from discord.ext import commands
from discord.utils import get

from datetime import timedelta

import function as func
from function import infoGameFromShop
from function import WorkDataBase as WorkDB
import json
import requests
from requests.exceptions import HTTPError

import epic_mod
import time
import random
import sqlite3
import datetime
import asyncio
#CONFIG
bot = commands.Bot(command_prefix='!')
conn = sqlite3.connect("Discord.db")
cursor = conn.cursor()
WorkDB = WorkDB() 
powered = "powered by MAXIM"
mainGuildId = 412939700748419084
mainGuildUrl = "https://discord.gg/GmYNePW"
#CONFIG

# cursor.execute(f'CREATE TABLE "AllRequest" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"Request" TEXT, "status" TEXT, "nameShop" TEXT, "nameGame" TEXT, "price" TEXT,"urlGame" TEXT, "date" DATE)')
mainLoopStatus = False  # Variable which starts or stops the main loop

dataConfig = None  # Loaded configuration
langM = None

def EpicGamesFreeGame():
	global mainLoopStatus
	global dataConfig  # Gets config values
	global langM

	# await ctx.send(str(langM["start_success"]))

	# Here is where the real function starts

	mainLoopStatus = True  # Changes It to True so the main loop can start
	allNameGame = ""

	# Epic Games methods
	epic_mod.obj.make_request()
	epic_mod.obj.process_request()
	print(epic_mod.obj.gameData)
	allGameInfo = epic_mod.obj.gameData
	if len(allGameInfo) == 1:
		embed=discord.Embed(title="Бесплатные игры в Epic Games | Store", description=f"Привет всем участникам канала!\nСейчас в магазине Epic Games | Store бесплатно раздается: ``{allGameInfo[0][0]}``\n\nДанная игра будет бесплатна до {allGameInfo[0][2]}, успей добавить ее в свою библиотеку!\n[Ссылка на игру]({allGameInfo[0][1]})", color=0xff7d25)
	else:
		# Собираем список игр
		for GameInfo in allGameInfo:
			if allNameGame != "":
				allNameGame = allNameGame+"`` "+GameInfo[0]+" ``\n"
			else:
				allNameGame = "`` "+GameInfo[0]+" ``\n"
		# Собираем список игр
		embed=discord.Embed(title="Бесплатные игры в Epic Games | Store", description=f"Привет всем участникам канала!\nСейчас в магазине Epic Games | Store бесплатно раздаются: {allNameGame}\nДанные игры будут бесплатны до {allGameInfo[0][2]}, успей добавить их в свою библиотеку!\n[Ссылка на игры](https://www.epicgames.com/store/ru/free-games)", color=0xff7d25)
	embed.set_image(url=allGameInfo[random.randint(0,len(allGameInfo)-1)][3])
	embed.set_footer(text="Сервер "+str(bot.guilds[0].name))
	# print(str(ctx.channel.id))
	return embed

def sleepOneHours():
	todayNew = datetime.datetime.today()
	todayM = int(todayNew.strftime("%M"))
	sleepHOne = 3600 - (todayM * 60)
	return sleepHOne

async def freeSteamInfo():
	while not bot.is_closed():
		await bot.wait_until_ready()
		todayNew = datetime.datetime.today()
		todayWeekDay = str(todayNew.strftime("%A"))
		todayH = int(todayNew.strftime("%H"))
		todayM = int(todayNew.strftime("%M"))
		if todayH < 24: #if todayH + 5 < 24: 
			todayH = todayH #todayH = todayH + 5
		else:
			todayH = todayH - 24 #todayH = todayH + 5 - 24
		if todayWeekDay == 'Sunday': #Monday
			if todayH == 15: # and todayM == 0
				driver = func.chromeOpen()
				allInfo = func.freeSteam(driver)
				driver.close()
				if allInfo != None:
					embed=discord.Embed(title=allInfo["nameNews"], description=allInfo["titleNews"], color=0x3498e2)
					embed.set_image(url=allInfo["imageNews"])
					for Guild in bot.guilds:
						if Guild.id != mainGuildId:
							embed.set_author(name=powered, url=mainGuildUrl) 
						embed.set_footer(text=str(Guild.name))
						channel = bot.get_channel(Guild.system_channel.id)
						await channel.send(embed=embed)
						await asyncio.sleep(2)

				await asyncio.sleep(int(sleepOneHours()))
			else:
				await asyncio.sleep(int(sleepOneHours()))
		else:
			await asyncio.sleep(int(sleepOneHours()))


def freeSteamInfoHandmade(idChannel):
	channel = bot.get_channel(idChannel)
	Guild = channel.guild
	driver = func.chromeOpen()
	allInfo = func.freeSteam(driver)
	driver.close()
	embed=discord.Embed(title=allInfo["nameNews"], description=allInfo["titleNews"], color=0x3498e2)
	embed.set_image(url=allInfo["imageNews"])
	if Guild.id != mainGuildId:
		embed.set_author(name=powered, url=mainGuildUrl) 
	embed.set_footer(text=str(Guild.name))
	return embed
		


@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))

@bot.command()
@commands.has_permissions(administrator=True)
async def EGS(ctx):
	embed = EpicGamesFreeGame()
	await ctx.send(embed=embed)

@bot.command()
async def freegame(ctx):
	embed = freeSteamInfoHandmade(ctx.message.channel.id)
	await ctx.send(embed=embed)

@bot.command(pass_context= True)
async def price(ctx, *, nameGame):
	WorkDB.deleteOldRequest() # Удаление старых запросов
	embed=discord.Embed(title="Проверка цен на игры", description="Проверка по запросу '"+nameGame+"'", color=0x3498e2)
	embed.set_thumbnail(url="https://media.discordapp.net/attachments/696376496582950953/727133792912801853/best.png")
	driver = func.chromeOpen()
	infoShopZakaZaka = WorkDB.checkRequestInfoGame(nameGame, "Zaka-Zaka.com")
	if infoShopZakaZaka == None:
		infoShopZakaZaka = func.checkZakaZaka(nameGame, driver)

	infoShopSteamPay = WorkDB.checkRequestInfoGame(nameGame, "SteamPay.com")
	if infoShopSteamPay == None:
		infoShopSteamPay = func.checkSteamPay(nameGame, driver)

	infoShopSteamBuy = WorkDB.checkRequestInfoGame(nameGame, "SteamBuy.com")
	if infoShopSteamBuy == None:
		infoShopSteamBuy = func.checkSteamBuy(nameGame, driver)

	infoShopSteam = WorkDB.checkRequestInfoGame(nameGame, "Steam.com")
	if infoShopSteam == None:
		infoShopSteam = func.checkSteam(nameGame, driver)

	infoShopEpicGames = WorkDB.checkRequestInfoGame(nameGame, "EpicGames.com")
	if infoShopEpicGames == None:
		infoShopEpicGames = func.checkEpicGames(nameGame, driver)

	driver.close()
	if infoShopZakaZaka.status == "Success":
		embed.add_field(name=str(infoShopZakaZaka.nameShop)+" `` "+str(infoShopZakaZaka.price)+" ``", value="["+str(infoShopZakaZaka.nameGame)+"]("+str(infoShopZakaZaka.urlGame)+")", inline=False)
	if infoShopZakaZaka.status == "Out of stock":
		embed.add_field(name=str(infoShopZakaZaka.nameShop)+" `` Нет в наличии ``", value="["+str(infoShopZakaZaka.nameGame)+"]("+str(infoShopZakaZaka.urlGame)+")", inline=False)
	if infoShopZakaZaka.status == "No information":
		embed.add_field(name=str(infoShopZakaZaka.nameShop), value="Нет информации", inline=False)

	if infoShopSteamPay.status == "Success":
		embed.add_field(name=str(infoShopSteamPay.nameShop)+" `` "+str(infoShopSteamPay.price)+" ``", value="["+str(infoShopSteamPay.nameGame)+"]("+str(infoShopSteamPay.urlGame)+")", inline=False)
	if infoShopSteamPay.status == "Out of stock":
		embed.add_field(name=str(infoShopSteamPay.nameShop)+" `` Нет в наличии ``", value="["+str(infoShopSteamPay.nameGame)+"]("+str(infoShopSteamPay.urlGame)+")", inline=False)
	if infoShopSteamPay.status == "No information":
		embed.add_field(name=str(infoShopSteamPay.nameShop), value="Нет информации", inline=False)

	if infoShopSteamBuy.status == "Success":
		embed.add_field(name=str(infoShopSteamBuy.nameShop)+" `` "+str(infoShopSteamBuy.price)+" ``", value="["+str(infoShopSteamBuy.nameGame)+"]("+str(infoShopSteamBuy.urlGame)+")", inline=False)
	if infoShopSteamBuy.status == "Out of stock":
		embed.add_field(name=str(infoShopSteamBuy.nameShop)+" `` Нет в наличии ``", value="["+str(infoShopSteamBuy.nameGame)+"]("+str(infoShopSteamBuy.urlGame)+")", inline=False)
	if infoShopSteamBuy.status == "No information":
		embed.add_field(name=str(infoShopSteamBuy.nameShop), value="Нет информации", inline=False)

	if infoShopSteam.status == "Success":
		embed.add_field(name=str(infoShopSteam.nameShop)+" `` "+str(infoShopSteam.price)+" ``", value="["+str(infoShopSteam.nameGame)+"]("+str(infoShopSteam.urlGame)+")", inline=False)
	if infoShopSteam.status == "Out of stock":
		embed.add_field(name=str(infoShopSteam.nameShop)+" `` Нет в наличии ``", value="["+str(infoShopSteam.nameGame)+"]("+str(infoShopSteam.urlGame)+")", inline=False)
	if infoShopSteam.status == "No information":
		embed.add_field(name=str(infoShopSteam.nameShop), value="Нет информации", inline=False)

	if infoShopEpicGames.status == "Success":
		embed.add_field(name=str(infoShopEpicGames.nameShop)+" `` "+str(infoShopEpicGames.price)+" ``", value="["+str(infoShopEpicGames.nameGame)+"]("+str(infoShopEpicGames.urlGame)+")", inline=False)
	if infoShopEpicGames.status == "Out of stock":
		embed.add_field(name=str(infoShopEpicGames.nameShop)+" `` Нет в наличии ``", value="["+str(infoShopEpicGames.nameGame)+"]("+str(infoShopEpicGames.urlGame)+")", inline=False)
	if infoShopEpicGames.status == "No information":
		embed.add_field(name=str(infoShopEpicGames.nameShop), value="Нет информации", inline=False)

		

	embed.set_footer(text="Lounge Zone")
	await ctx.send(embed=embed)




@bot.command()
@commands.has_permissions(administrator=True)
async def db(ctx):
	global cursor
	global conn
	# cursor.execute('DROP TABLE user_activity')
	# cursor.execute('DROP TABLE AllRequest')
	# cursor.execute(f'CREATE TABLE "AllRequest" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"Request" TEXT, "status" TEXT, "nameShop" TEXT, "nameGame" TEXT, "price" TEXT,"urlGame" TEXT, "date" DATE)')
	# cursor.execute(f"INSERT INTO AllRequest (Request, status, nameShop, nameGame, price, urlGame, date) VALUES ('GameReq','Zaka-Zaka', 'Success', 'NameGame', '100', 'https//google.com', date('now'))")
	# print("====================")
	# for row in cursor.execute(f"SELECT * FROM AllRequest"):
	# 	print(str(row[0])+"\t"+str(row[1])+"\t"+str(row[2])+"\t"+str(row[3])+"\t"+str(row[4])+"\t"+str(row[5])+"\t"+str(row[6])+"\t"+str(row[7]))
	# print("====================")
	# cursor.execute(f'CREATE TABLE "AppConfig" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"lastNewsFreeSteam" TEXT)')
	# cursor.execute(f"INSERT INTO AppConfig (lastNewsFreeSteam) VALUES ('NoneText')")
	# cursor.execute(f'CREATE TABLE "usersOnTheChannel" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"id_guild" MEDIUMINT,"id_user", "date_time" DATETIME)')
	cursor.execute(f'CREATE TABLE "user_activity" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"id_guild" MEDIUMINT,"id_user" MEDIUMINT, "connect_activity" MEDIUMINT)')
	conn.commit()

@bot.command()
@commands.has_permissions(administrator=True)
async def info(ctx):
	embed = func.infoСommand()
	await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def stats(ctx, id_guild):
	global bot
	Image = func.creatingImageStats(id_guild, bot)
	await ctx.send(file=Image)


# СОБЫТИЯ DISCORD
@bot.event
async def on_member_update(before, after):
	print(str(before.activities))
	# func.timeSpentOnTheGame(before.activity, before.activity[0].game)
	# if after.activity != None:
	# 	newGameStatus = after.activity.name

@bot.event
async def on_voice_state_update(member, before, after):
	func.timeSpentOnTheChannel(member, before, after)



# СОБЫТИЯ DISCORD
	

# @bot.event
# async def on_message(message):
#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')

token = "NzI2Nzk3MDQwMDQ2MDQ3MzAz.XvihDQ.M929Me95TPMXZAp_LWW4hq3464k"
bot.bg_task = bot.loop.create_task(freeSteamInfo())
# bot.bg_task = bot.loop.create_task(goodMorning())
# bot.bg_task = bot.loop.create_task(freeGameEpic())
# bot.bg_task = bot.loop.create_task(checkCrackGame())
# bot.bg_task = bot.loop.create_task(newsGamePlayGround())
# bot.bg_task = bot.loop.create_task(deleteVoiceChannel())
bot.run(os.environ.get('BOT_TOKEN'))

