from selenium import webdriver
import time
import re
from playsound import playsound
import pickle
from peewee import *

def main():
	USER_LOGIN = ''
	USER_PASSWORD = ''
	#options = webdriver.ChromeOptions()
	#options.add_argument('window-size=1366x768')
	#options.add_argument('headless')
	#driver = webdriver.Chrome(options=options)
	driver = webdriver.Firefox()
	driver.set_window_size(1366,768)
	driver.get('https://www.upwork.com/ab/account-security/login')
	pickle.dump(driver.get_cookies(), open('cookies.pkl', 'wb'))
	cookies = pickle.load(open('cookies_f.pkl', 'rb'))
	for cookie in cookies:
		driver.add_cookie(cookie)
	time.sleep(5)
	try:
		email = driver.find_element_by_id('login_username')
		email.send_keys(USER_LOGIN)
	except:
		print('Cannot load page. Captcha!')
	btn = driver.find_element_by_xpath('//div[@class="text-center flex-1 "]//div[@class="col-md-10 col-md-offset-1 "]//button')
	btn.click()
	time.sleep(3)
	p = driver.find_element_by_id('login_password')
	p.send_keys(USER_PASSWORD)
	btn = driver.find_element_by_xpath('//div[@class="flex-1 "]//div[@class="col-md-10 col-md-offset-1 "]//button')
	btn.click()
	time.sleep(3)

	db = SqliteDatabase('db.db')

	class Data(Model):
		url = TextField()

		class Meta:
			database = db

	db.connect()
	db.create_tables([Data])

	pattern = r'scrap|pars|snif|crawl|парс|captcha|wordpress'
	count = 0
	while(True):
		try:
			n = driver.find_element_by_xpath('//div[@class="col-md-8"]//div[@class="ng-scope"]//button')
			n.click()
		except:
			pass
		time.sleep(5)
	
		sections = driver.find_elements_by_xpath('//div[@id="feed-jobs"]//section')
		for section in sections:
			name = section.find_element_by_tag_name('h4').text.strip()
			link = section.find_element_by_tag_name('h4').find_element_by_tag_name('a').get_attribute('href')
			try:
				price = section.find_element_by_class_name('col-md-12').find_element_by_css_selector('small span:nth-child(3) span:nth-child(2)').text
			except:
				price = ''
			descr = section.find_element_by_class_name('description').text.strip()
			
			exists = Data.select().where(Data.url == link).count()
			if exists < 1:
				db.execute_sql('insert or ignore into data(url) values ("{}")'.format(link))
				if(len(re.findall(pattern, name))>0 or len(re.findall(pattern, descr))>0):
					print(name)
					print(price)
					print(link)
					print(descr)
					now = time.strftime('%d %b %Y %H:%M:%S', time.localtime())
					print(now)
					playsound('job.mp3')

		time.sleep(60)
		count = count+1
		print(count)
		if count == 30:
			count = 0
			Data.truncate_table()
			driver.refresh()
			time.sleep(5)
		
		


if __name__ == '__main__':
	main()
