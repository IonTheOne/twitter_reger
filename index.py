import time, os
import json
import requests
import names
import random
from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from SeleniumAuthProxy import SeleniumAuthProxy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from modules.SMSHUB import SMSHUBapi
from selenium.common.exceptions import NoSuchElementException
from password_generator import PasswordGenerator


try:
    # re = "\033[1;31m"
    # gr = "\033[1;32m" 194.67.214.134:9947:THmek8:g9bdeS
    # country = input(gr+"[+] enter country code : "+re)186.65.117.254:9623:CYqAsr:Hz46qW
    proxy = SeleniumAuthProxy.get_proxy_object("186.65.117.254", "9623", "CYqAsr", "Hz46qW", "proxy")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
    chrome_options = Options()
    notifications = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", notifications)
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=" + user_agent)
    chrome_options.add_argument('--lang=en')
    chrome_options.add_argument("--start-maximized");
    chrome_options.add_extension(proxy)


    browser = Chrome(executable_path="assets/chromedriver.exe", options=chrome_options)
    sms_hub = SMSHUBapi("")
    balance = sms_hub.get_balance()
    print(f"Мой баланс: {balance}")

    browser.get("https://twitter.com/")
    browser.find_element_by_link_text("Sign up").click()
    time.sleep(5)
    name_for_reg = names.get_full_name(gender='female')

    browser.find_element_by_css_selector('input[name="name"]').send_keys(name_for_reg)
    time.sleep(2)
    month_for_reg = random.randint(1, 12)
    day_for_reg = random.randint(1, 28)
    year_for_reg = str(random.randint(1978, 1998))

    month_for_reg_box = Select(browser.find_element_by_id('Month'))
    month_for_reg_box.select_by_index(month_for_reg)
    time.sleep(2)
    day_for_reg_box = Select(browser.find_element_by_id('Day'))
    day_for_reg_box.select_by_index(day_for_reg)
    time.sleep(2)
    year_for_reg_box = Select(browser.find_element_by_id('Year'))
    year_for_reg_box.select_by_value(year_for_reg)
    time.sleep(2)

    if balance >= 2:
     # Заказываем номер

        country_codes = random.choice([2, 0, 102, 34, 36, 73])
        print(f"Код страны - {country_codes}")
        try:
            phone_id, phone_num = sms_hub.get_number(service='tw', operator='any', country=country_codes)
        except TypeError:
            time.sleep(7)
            print("Error - не получили номер от смс активатора")
            browser.close()
            os.system("python index.py")
        print(f"Получили номер: {phone_num}")

        browser.find_element_by_css_selector('input[name="phone_number"]').send_keys(f"+{phone_num}")
        time.sleep(5)
        print("OK")

    browser.implicitly_wait(5)

    btn_exists = browser.find_element_by_css_selector('div[role="button"]').get_attribute("aria-disabled")
    if btn_exists == "true":
        sms_hub.set_status(phone_id, 8)
        print("Error - неподходящий номер")
        browser.close()
        os.system("python index.py")
    else:
        browser.find_element_by_css_selector('div[role="button"]').click()
    time.sleep(2)
    browser.find_element_by_xpath("//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div/div/span/span").click()
    time.sleep(2)
    browser.find_element_by_xpath("//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/div").click()
    time.sleep(2)
    browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div[3]/div[2]/div").click()

    try:
        if browser.find_element_by_css_selector('div[role="alert"]'):
            time.sleep(3)
            sms_hub.set_status(phone_id, 8)
            print("Can't send SMS on this phone")
            browser.close()
            os.system("python index.py")


    except:
        time.sleep(1)
    finally:
        time.sleep(1)

    #Начинаем принимать СМС-ку

    sms_hub.set_status(phone_id, 1)


    def get_code(wait=1, max_wait=30):
        wait_time = 0

        for i in range(max_wait):
            # Получаем статус СМС
            wait_time += wait
            status = sms_hub.get_status(phone_id)
            time.sleep(2)
            print(f"{status[0]} - прошло {wait_time} cекунд")
            # Если код был прислан
            if status[0] == 'STATUS_OK':
                return status
        if wait_time >= max_wait:
            print(f"Timeout: {max_wait} seconds")
            print("Запрашиваем повтороное СМС")
            browser.find_element_by_xpath("//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div[2]/div/div/div/div/span/span[2]").click()
            time.sleep(1)
            sms_hub.set_status(phone_id, 3)
            browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div[2]/div[3]/div/div/div/div[2]/div/div/span").click()
            for i in range(max_wait):
                # Получаем статус СМС
                wait_time += wait
                status = sms_hub.get_status(phone_id)
                time.sleep(2)
                print(f"{status[0]} - прошло {wait_time} cекунд")
                # Если код был прислан
                if status[0] == 'STATUS_OK':
                    return status
                elif wait_time == 50:
                    sms_hub.set_status(phone_id, 8)
                    print("Не дождались СМС")
                    time.sleep(2)
                    browser.close()
                    os.system("python index.py")

        return None

    code = get_code()
    print(f"Получили код: {code[1]}")
    time.sleep(2)
    sms_code_input = browser.find_element_by_css_selector('input[name="verfication_code"]').send_keys(code[1])
    time.sleep(3)
    browser.find_element_by_xpath("//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div/div/span/span").click()
    time.sleep(6)
    #Генерим пароль
    pwo = PasswordGenerator()
    pwo.minlen = 10  # (Optional)
    pwo.maxlen = 12  # (Optional)
    password = pwo.generate()
    password_input = browser.find_element_by_css_selector('input[name="password"]').send_keys(password)
    time.sleep(6)
    browser.find_element_by_xpath("//*[@id='layers']/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div/div/span").click()
    time.sleep(6)
    #Работа и загрузка Аватарки

    path = r"D:\Arba\BAS автоматизация истоков\ACC sale\PACK TELOK1"
    random_filename = random.choice([
        x for x in os.listdir(path)
        if os.path.isfile(os.path.join(path, x))
    ])
    from PIL import Image
    thread = random.randint(1,10000)
    image = Image.open(f"{random_filename}")
    image.thumbnail((300, 300))
    image.save(f"{thread}.jpg")
    print(image)
    avatar = browser.find_element_by_xpath("//input[@data-testid='fileInput']")
    time.sleep(2)
    # file path specified with send_keys
    avatar.send_keys(f"{thread}.jpg")
    time.sleep(2)
    browser.find_element_by_xpath("//*[@id='layers']/div[2]/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[3]/div").click()
    time.sleep(5)
    browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div").click()
    time.sleep(3)
    os.remove(f"{thread}.jpg")
    #Bio generate

    get_bio = requests.get("http://www.twitterbiogenerator.com/generate")
    bio = get_bio.text
    browser.find_element_by_css_selector('textarea[name="text"]').send_keys(bio)
    time.sleep(3)
    browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div").click()
    time.sleep(3)
    #Interests generate
    if browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div"):
        browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div").click()
        time.sleep(3)
    elif browser.find_element_by_link_text("Skip for now"):
        browser.find_element_by_link_text("Skip for now").click()
        time.sleep(3)
    # Following before registration
    time.sleep(7)
    if browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div"):
        browser.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div/div[3]/div").click()
        time.sleep(3)
    elif browser.find_element_by_link_text("Next"):
        browser.find_element_by_link_text("Next").click()
        time.sleep(3)
    #Connect to acc
    time.sleep(20)
    browser.find_element_by_css_selector('a[aria-label="Profile"]').click()
    # Сохраянем данные аккаунта
    profile_twitter = browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/span")
    profile = profile_twitter.text
    print(f"{profile}:+{phone_num}:{password}")
    time.sleep(3)
    os.mkdir(f"{profile}")
    with open(f"{profile}\{profile}.txt", 'w') as f:
        f.write(f"{profile}:+{phone_num}:{password}")
    with open(f"{profile}\cookies.txt", 'w') as c:
        c.write("1")
    time.sleep(5)
    browser.find_element_by_css_selector('a[aria-label="Home"]').click()
    time.sleep(5)
    #Tweet generator
    get_tweet = requests.get("https://randomwordgenerator.com/json/sentences.json")
    bio = json.loads(get_tweet.text)
    gen_tweet_num = random.randint(1, 10)
    for s in bio.items():
        tweet = s[1][gen_tweet_num]['sentence']
        print(f"Отправляем твит - {tweet}")
    #Send tweet
    browser.find_element_by_css_selector('div[aria-label="Tweet text"]').send_keys(tweet)
    time.sleep(3)
    #####Задать правильный путь к кнопке Твит
    if browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[4]/div/div/div[2]/div[3]"):
        browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[4]/div/div/div[2]/div[3]").click()
        time.sleep(5)
    elif browser.find_element_by_link_text("Tweet"):
        browser.find_element_by_link_text("Tweet").click()
        time.sleep(5)
    browser.find_element_by_css_selector('a[aria-label="Profile"]').click()
    time.sleep(5)
    browser.find_element_by_css_selector('a[aria-label="Home"]').click()
    time.sleep(5)
    browser.execute_script("window.scrollTo(0, 2000)")
    time.sleep(7)
    try:
        if browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[4]/div/div/section/div/div/div[9]/div/a"):
            browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[4]/div/div/section/div/div/div[9]/div/a").click()
    except:
        if browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[4]/div/div/section/div/div/div[8]/div/a"):
            browser.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[4]/div/div/section/div/div/div[8]/div/a").click()
    time.sleep(7)
    # #Make Following
    # contents = browser.find_elements_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div[3]/div/div/div/div[2]/div[1]/div[2]/div")
    # t = 5
    # for t in contents:
    #     t.click()
    #     time.sleep(15)
    #     t += 1
    print(profile)
    browser.execute_script("window.scrollTo(0, 2000)")
    time.sleep(3)
    browser.execute_script("window.scrollTo(0, 4000)")
    time.sleep(3)
    browser.execute_script("window.scrollTo(0, 6000)")
    browser.find_elements_by_xpath(f"//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div[25]/div/div/div/div[2]/div[1]/div[2]/div/div/span/span").click()
    time.sleep(2)
    browser.find_elements_by_xpath(f"//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div[27]/div/div/div/div[2]/div[1]/div[2]/div/div/span/span").click()
    time.sleep(2)
    browser.execute_script("window.scrollTo(0, 8000)")
    time.sleep(3)
    browser.find_elements_by_xpath(f"//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div[29]/div/div/div/div[2]/div[1]/div[2]/div/div/span/span").click()
    time.sleep(2)
    browser.execute_script("window.scrollTo(0, 7000)")
    follow_num = random.randint(30, 40)
    for count in range(26, follow_num):
        browser.find_element_by_xpath(f"//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div[{count}]/div/div/div/div[2]/div[1]/div[2]/div/div/span/span").click()
        time.sleep(3)
    browser.find_element_by_css_selector('a[aria-label="Profile"]').click()


    # for i in range(3, 10):
    #     browser.find_element_by_xpath(f"//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/section/div/div/div[{i}]/div/div/div[2]/div[2]/div[1]/div[2]/div").click()
    #

    time.sleep(15)


finally:

    print("Yes")
