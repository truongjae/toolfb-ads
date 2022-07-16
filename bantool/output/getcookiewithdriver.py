from time import sleep as sl
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup as BS
from requests import session
import random
from random import randint as ri
import requests
import mechanize

import threading

count_add_card_success=0
count_list_clone = 0
list_acc_fb_dtsg = []
count_setting_acc_success=0
class Card:
	def __init__(self,code,date,ccv):
		self.code = code
		self.date = date
		self.ccv = ccv

class Acc:
	def __init__(self,tk,mk,fa,cookies):
		self.tk = tk
		self.mk = mk
		self.fa = fa
		self.cookies = cookies
class AccFbdtsg:
	def __init__(self,cookies,fb_dtsg,account_id):
		self.cookies = cookies
		self.fb_dtsg = fb_dtsg
		self.account_id = account_id

def convert_cookie_to_json(string_cookie):
	temp= string_cookie.replace(" ", "")
	temp = temp.split(";")
	listKey = ["sb","datr","c_user","xs","fr"]
	listCookies = []
	for i in temp:
		key = i.split("=")[0]
		if key in listKey:
			listCookies.append(i)
	string_cookie=";".join(listCookies)
	try:
		cookie = SimpleCookie()
		cookie.load(string_cookie)
		cookies = {}
		for key, morsel in cookie.items():
		    cookies[key] = morsel.value
		return cookies
	except:
		return ""

def get2FA(fa):
	p = requests.get("https://2fa.live/tok/"+fa)
	return p.json()['token']



def login(email,pw,fa):
	browser = mechanize.Browser()
	browser.set_handle_robots(False)
	cookies = mechanize.CookieJar()
	browser.set_cookiejar(cookies)
	browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
	browser.set_handle_refresh(False)
	url = 'http://m.facebook.com/login.php'
	browser.open(url)
	browser.select_form(nr = 0)
	browser.form['email'] = email
	browser.form['pass'] = pw
	response = browser.submit()

	browser.open("https://m.facebook.com/checkpoint/?__req=7")
	browser.select_form(nr = 0)
	browser.form['approvals_code'] = get2FA(fa)
	response = browser.submit()

	for i in range(3):
		try:
			browser.open("https://m.facebook.com/login/checkpoint/")
			browser.select_form(nr = 0)
			response = browser.submit()
		except:
			pass

	return str(browser._ua_handlers['_cookies'].cookiejar)
	


def getCookie(listCookies):
	listCookies = listCookies.split("CookieJar")
	listCookies = listCookies[1]
	listCookies = listCookies[1:len(listCookies)-2]
	listCookies = " "+listCookies
	listCookies = listCookies.split(",")
	result = ""
	for cookie in listCookies:
		temp = cookie.split(" ")
		if temp[2]!="noscript=1":
			result+=temp[2]+";"
	result = result[0:len(result)-1]
	return result


print(getCookie(login("100083592660167","P0WwEnI")))