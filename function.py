import discord
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re
from PIL import Image, ImageDraw, ImageFont
import sys
import datetime

conn = sqlite3.connect("Discord.db")
cursor = conn.cursor()

class infoGameFromShop(object):
	def __init__(self, nameShop = "None", status = "None", nameGame = "None", price = "None", urlGame = "None"):
		super(infoGameFromShop, self).__init__()
		self.nameShop 	= nameShop
		self.status 	= status
		self.nameGame	= nameGame
		self.price 		= price
		self.urlGame 	= urlGame

class WorkDataBase(object):
	def __init__(self):
		self.conn = sqlite3.connect("Discord.db")
		self.cursor = self.conn.cursor()

	def checkRequestInfoGame(self, nameGame, nameShop):#infoGame
		cursor = self.cursor
		infoGameFromDB = cursor.execute(f"SELECT * FROM AllRequest where Request='{nameGame}' AND nameShop='{nameShop}' LIMIT 1")
		if infoGameFromDB.fetchone() != None:
			print("Есть инф в БД")
			for infoGameFromDB in cursor.execute(f"SELECT * FROM AllRequest where Request='{nameGame}' AND nameShop='{nameShop}' LIMIT 1"):
				infoGame = infoGameFromShop()
				infoGame.nameShop = infoGameFromDB[3]
				infoGame.status = infoGameFromDB[2]
				infoGame.nameGame = infoGameFromDB[4]
				infoGame.price = infoGameFromDB[5]
				infoGame.urlGame = infoGameFromDB[6]
				return infoGame
			return None
		else:
			return None

	def deleteOldRequest(self):
		try:
			self.cursor.execute(f"DELETE FROM AllRequest WHERE date < datetime('now','-14 day')")
			self.conn.commit()
		except:
			pass

	def addInfoInDB(self,request, infoGame):
		try:
			self.cursor.execute(f"INSERT INTO AllRequest (request, status, nameShop, nameGame, price, urlGame, date) VALUES ('{request}', '{infoGame.status}', '{infoGame.nameShop}', '{infoGame.nameGame}', '{infoGame.price}', '{infoGame.urlGame}', date('now'))")
			self.conn.commit()
		except:
			pass

def chromeOpen():
	driver = webdriver.Chrome('D:\\pythonCODE\\discordBotV2\\Resource\\chromedriver.exe')
	return driver

def soarchAvailGame(response):
	print(len(response))
	for game in response:
		if game['available'] == 1:
			return game
	return None

def checkZakaZaka(nameGame, driver):
	WorkDB = WorkDataBase()
	requestNameGame = nameGame
	infoGame = infoGameFromShop()
	infoGame.nameShop = "Zaka-Zaka.com"
	driver.get("https://zaka-zaka.com/search/ask/"+nameGame+"/sort/date.desc")
	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='search-results']/a[@class='game-block']"))) #Первая ссылка из списка
	except:
		infoGame.status = "No information"
		return infoGame

	urlShopThisGame = element.get_attribute('href')
	try:
		nameGame = driver.find_element_by_xpath("//div[@class='game-block-name']").get_attribute("textContent")
	except:
		pass
	try:
		price = re.sub("\D","",driver.find_element_by_xpath("//div[@class='game-block-price']").get_attribute("textContent"))
		
	except:
		price = False
	if price:
		infoGame.status = "Success"
		infoGame.nameGame = nameGame
		infoGame.price = price+" ₽"
		infoGame.urlGame = urlShopThisGame+"/?agent=e480a2d6-1a01-4990-bc84-1909604a502e"
	else:
		infoGame.status = "Out of stock"
		infoGame.nameGame = nameGame
		infoGame.urlGame = urlShopThisGame+"/?agent=e480a2d6-1a01-4990-bc84-1909604a502e"

	WorkDB.addInfoInDB(requestNameGame, infoGame)
	return infoGame

def checkSteamPay(nameGame, driver):
	WorkDB = WorkDataBase()
	requestNameGame = nameGame
	infoGame = infoGameFromShop()
	infoGame.nameShop = "SteamPay.com"
	driver.get("https://steampay.com/search?q="+nameGame)


	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH , "//div[contains(@class, 'catalog') and contains(@class, 'catalog--main')]/a[1]"))) #Первая ссылка из списка
	except:
		infoGame.status = "No information"
		return infoGame

	urlShopThisGame = element.get_attribute('href')
	try:
		nameGame = element.find_element_by_xpath("//div[@class='catalog-item__name']").get_attribute("textContent").replace('\n', '')
	except:
		pass
	try:
		price = re.sub("\D","", element.find_element_by_xpath("//span[@class='catalog-item__price-span']").get_attribute("textContent"))
	except:
		price = False

	if price:
		infoGame.status = "Success"
		infoGame.nameGame = nameGame
		infoGame.price = price+" ₽"
		infoGame.urlGame = urlShopThisGame+"/?agent=21f8ae31-3aa9-4c2a-aa0b-f16932ec12e8"
	else:
		infoGame.status = "Out of stock"
		infoGame.nameGame = nameGame
		infoGame.urlGame = urlShopThisGame+"/?agent=21f8ae31-3aa9-4c2a-aa0b-f16932ec12e8"
		
	WorkDB.addInfoInDB(requestNameGame, infoGame)
	return infoGame

def checkSteamBuy(nameGame, driver):
	WorkDB = WorkDataBase()
	requestNameGame = nameGame
	infoGame = infoGameFromShop()
	infoGame.nameShop = "SteamBuy.com"
	driver.get("https://steambuy.com/catalog/?q="+nameGame)

	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH , "//div[@class='view-content']/div[@class='product-list']/div[contains(@class, 'product-item')][1]"))) #Первая игра из списка
	except:
		infoGame.status = "No information"
		return infoGame

	try:
		urlShopThisGame = element.find_element_by_xpath("//a[@class='product-item__img-link']").get_attribute('href')
	except:
		urlShopThisGame = "https://steambuy.com"
	try:
		nameGame = element.find_element_by_xpath("//a[@class='product-item__title-link']").get_attribute("textContent")
	except:
		pass
	try:
		price = re.sub("\D","",element.find_element_by_xpath("//div[@class='product-item__cost']").get_attribute("textContent"))
		
	except:
		price = False
	if price:
		infoGame.status = "Success"
		infoGame.nameGame = nameGame
		infoGame.price = price+" ₽"
		infoGame.urlGame = urlShopThisGame+"/partner/948732"
	else:
		infoGame.status = "Out of stock"
		infoGame.nameGame = nameGame
		infoGame.urlGame = urlShopThisGame+"/partner/948732"
	WorkDB.addInfoInDB(requestNameGame, infoGame)
	return infoGame

def checkSteam(nameGame, driver):
	WorkDB = WorkDataBase()
	requestNameGame = nameGame
	infoGame = infoGameFromShop()
	infoGame.nameShop = "Steam.com"
	driver.get("https://store.steampowered.com/search/?term="+nameGame)
	# driver.find_element_by_xpath("//input[@id='store_nav_search_term']").send_keys(nameGame)

	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH , "//div[@id='search_results']//a[1]"))) #Первая ссылка из списка
	except:
		infoGame.status = "No information"
		return infoGame

	urlShopThisGame = element.get_attribute('href')
	try:
		nameGame = element.find_element_by_xpath("//div[contains(@class, 'search_name')]//span[@class='title']").get_attribute("textContent")
	except:
		pass
	try:
		price = re.sub("\D","",element.find_element_by_xpath("//div[contains(@class, 'search_price')]").get_attribute("textContent"))
		if price == "":
			price = "0"
	except:
		price = False
	if price:
		infoGame.status = "Success"
		infoGame.nameGame = nameGame
		infoGame.price = price+" ₽"
		infoGame.urlGame = urlShopThisGame
	else:
		infoGame.status = "Out of stock"
		infoGame.nameGame = nameGame
		infoGame.urlGame = urlShopThisGame
	WorkDB.addInfoInDB(requestNameGame, infoGame)
	return infoGame

def checkEpicGames(nameGame, driver):
	WorkDB = WorkDataBase()
	requestNameGame = nameGame
	infoGame = infoGameFromShop()
	infoGame.nameShop = "EpicGames.com"
	driver.get("https://www.epicgames.com/store/ru/browse?pageSize=30&q="+nameGame+"&sortBy=relevance&sortDir=DESC")
	try:
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//section[starts-with(@class, 'Browse-gridContainer_')]"))) 
	except:
		print("1")
		infoGame.status = "No information"
		return infoGame
	try:
		element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH , "//section[starts-with(@class, 'Browse-gridContainer_')]//li[starts-with(@class, 'BrowseGrid-card_')][1]"))) #Первая ссылка из списка
	except:
		print("2")
		infoGame.status = "No information"
		# infoGame.append("Нет информации")
		return infoGame

	urlShopThisGame = element.find_element_by_xpath("//a").get_attribute('href')
	# driver.get(urlShopThisGame)
	try:
		nameGame = element.find_element_by_xpath("//span[starts-with(@class, 'OfferTitleInfo-title_')]").get_attribute("textContent")
	except:
		pass
	try:
		price = re.sub("\D,","",element.find_element_by_xpath("//span[starts-with(@class, 'Price-original_')]").get_attribute("textContent"))

		price = price[0:-2]
		if price == "":
			price = "0"
	except:
		price = False
	if price:
		infoGame.status = "Success"
		infoGame.nameGame = nameGame
		infoGame.price = price+" ₽"
		infoGame.urlGame = urlShopThisGame
	else:
		infoGame.status = "Out of stock"
		infoGame.nameGame = nameGame
		infoGame.urlGame = urlShopThisGame

	WorkDB.addInfoInDB(requestNameGame, infoGame)
	return infoGame
	

def freeSteam(driver):
	driver.get("https://freesteam.ru/category/active/")
	try:
		urlGamePreview = driver.find_element_by_xpath("//div[@id='blog-grid']//div[contains(@class, 'post-box')]//a[@rel='bookmark']").get_attribute('href')
	except:
		print("1")
		return None

	driver.get(urlGamePreview)
	try:
		nameNews = driver.find_element_by_xpath("//h1[@class='entry-title']").get_attribute("textContent")
		if nameNews.lower().find("epic") != -1:
			print("Данная новость про Epic Games!")
			return None
		titleNews = driver.find_element_by_xpath("//div[@class='entry-content']").get_attribute("textContent")
		imageNews = driver.find_element_by_xpath("//img[contains(@class, 'wp-post-image')]").get_attribute("src")
		p = re.compile(r'<img.*?/>')
		titleNews = p.sub('', titleNews)
		titleNews = re.sub('\n+', '\n\n',titleNews)
		titleNews = titleNews+"\n[Ссылка на источкник]("+urlGamePreview+")"
		allInfo = dict(nameNews=nameNews, titleNews=titleNews, imageNews=imageNews,)
	except:
		return None

	return allInfo


def infoСommand():
	embed=discord.Embed(title="Команды для бота", color=0xff7d25)
	embed.add_field(name="Проверка цен на игру", value="`` !price [название игры] ``\nЦены проверяются из магазинов - Zaka-Zaka.com, SteamPay.com, SteamBuy.com, Steam.com, EpicGames.com.", inline=False)
	embed.add_field(name="Игры которые раздаются в Epic Games", value="`` !EGS ``\nБот отправляет информацию о бесплатных раздачах Epic Games каждую неделю автоматически, но вы можете запросить эту информацию в любой момент.", inline=False)
	embed.add_field(name="Бесплатные раздачи игр", value="`` !freegame ``\n Бот отправляет информацию о бесплатных раздачах из freesteam каждую неделю автоматически, но вы можете запросить эту информацию в любой момент.", inline=False)
	return embed

def creatingImageStats(id_guild, bot):
	global cursor
	global conn
	try:
		tatras = Image.open("stats.png")
	except:
		print("Unable to load image")
		return None
	    
	

	cursor.execute(f"SELECT * FROM user_activity WHERE id_guild = {int(id_guild)} ORDER BY connect_activity DESC LIMIT 3")
	allUserActivity = cursor.fetchall()
	if len(allUserActivity) != 0:
		index = 0
		idraw = ImageDraw.Draw(tatras)
		for userActivity in allUserActivity:
			topMargin = index * 85
			# ---------
			xRect = 157
			yRect = 140+topMargin
			idraw.rectangle((xRect, yRect, xRect+287, yRect+70), fill=(255, 255, 255))
			# ---------
			# ---------
			text = bot.get_user(userActivity[2]).name
			font = ImageFont.truetype('SFProDisplay-Medium.ttf', size=16)	 
			idraw.text((196, 153+topMargin), text, fill=(10, 10, 10), font=font)
			# ---------
			text = str(index + 1)
			font = ImageFont.truetype('SFProDisplay-Medium.ttf', size=16)	 
			idraw.text((170, 165+topMargin), text, fill=(111, 111, 111), font=font)
			# ---------
			# ---------
			text = "Активность:"
			font = ImageFont.truetype('SFProDisplay-Medium.ttf', size=15)	 
			idraw.text((196, 178+topMargin), text, fill=(138, 138, 138), font=font)
			# ---------
			# ---------
			text = ""
			a = userActivity[3]
			h=str(a//3600)
			m=(a//60)%60
			s=a%60
			if m<10:
			    m='0'+str(m)
			else:
			    m=str(m)
			if s<10:
			    s='0'+str(s)
			else:
			    s=str(s)

			if int(h)>0:
			   	text = text + h + "h "
			if int(m)>0:
			   	text = text + m + "m "

			text = text + s + "s "

			# text = f"{h}h {m}m {s}s"

			# date_time.mo
			# text = str(datetime.fromtimestamp(userActivity[3]).strftime("%A, %B %d, %Y %I:%M:%S"))
			font = ImageFont.truetype('SFProDisplay-Medium.ttf', size=15)	 
			idraw.text((285, 178+topMargin), text, fill=(10, 10, 10), font=font)
			# ---------
			index = index + 1

	nameImage = "Image.png"
	tatras.save(nameImage)
	file = discord.File(fp=nameImage)
	return file

def timeSpentOnTheChannel(member, before, after):
	conn = sqlite3.connect("Discord.db")
	cursor = conn.cursor()

	if after.channel != None:
		id_guild = after.channel.guild.id
		id_user = member.id
		cursor.execute(f"SELECT id FROM usersOnTheChannel WHERE id_guild = {id_guild} AND id_user = {id_user} ORDER BY id LIMIT 1")
		checkUserConnect = cursor.fetchall()
		if len(checkUserConnect) != 0:
			cursor.execute(f"DELETE FROM usersOnTheChannel WHERE id_guild = {id_guild} AND id_user = {id_user}")
		named_tuple = time.localtime()
		time_string = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
		cursor.execute(f"INSERT INTO usersOnTheChannel (id_guild, id_user, date_time) VALUES ({id_guild}, {id_user}, '{time_string}')")
		conn.commit()

	if before.channel != None and after.channel == None:
		id_guild = before.channel.guild.id
		id_user = member.id
		cursor.execute(f"SELECT date_time FROM usersOnTheChannel WHERE id_guild = {id_guild} AND id_user = {id_user} ORDER BY id LIMIT 1")
		checkUserConnect = cursor.fetchall()
		if len(checkUserConnect) != 0:
			timeStartConnect = datetime.datetime.strptime(checkUserConnect[0][0], "%Y-%m-%d %H:%M:%S")
			timeEndConnect = datetime.datetime.now()
			timeConnect = (timeEndConnect - timeStartConnect).seconds
			if timeConnect < 86400:
				cursor.execute(f"SELECT COUNT(*) FROM user_activity WHERE id_guild = {id_guild} AND id_user = {id_user}")
				countAccount = cursor.fetchall()
				print(str(timeConnect))
				if int(countAccount[0][0]) == 0:
					cursor.execute(f"INSERT INTO user_activity (id_guild, id_user, connect_activity) VALUES ({id_guild}, {id_user}, {timeConnect})")
					conn.commit()
				else:
					cursor.execute(f"UPDATE user_activity SET connect_activity = connect_activity + {timeConnect} WHERE id_guild = {id_guild} AND id_user = {id_user}")
			cursor.execute(f"DELETE FROM usersOnTheChannel WHERE id_guild = {id_guild} AND id_user = {id_user}")
			conn.commit()

def timeSpentOnTheGame(before, after):
	if after != None:
		print(after.game.name)
		print("START- "+after.game.start)
	if before != None:
		print(before.game.name)
		print("END- "+before.game.end)
	# if before.game == None and after.game == None:
	# 	pass






		
		
