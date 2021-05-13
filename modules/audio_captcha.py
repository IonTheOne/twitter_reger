import random
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import sys
import time
import requests
# from SeleniumAuthProxy import SeleniumAuthProxy


audioToTextDelay = 10
delayTime = 2
audioFile = "playload.mp3"
URL = "https://google.com/recaptcha/api2/demo"
SpeechToTextURL = "https://speech-to-text-demo.ng.bluemix.net"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"

def delay():
    time.sleep(random.randint(2, 3))

def audioToText(audiofile):
    driver.execute_script('''window.open("", "_black")''')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(SpeechToTextURL)

    delay()
    audioInput = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    audioInput.send_keys(audioFile)

    time.sleep(audioToTextDelay)

    text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')
    while text is None:
        text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')

    result = text.text

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result

try:
    # proxy = SeleniumAuthProxy.get_proxy_object("186.65.118.124", "9903", "cA3Xje", "bnCYoW", "proxy")
    options = webdriver.ChromeOptions()
    options.add_argument('--display-notifications')
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=" + user_agent)
    # options.add_extension(proxy)
    driver = webdriver.Chrome(executable_path="C:/Users/Denis/Desktop/chromedriver/chromedriver.exe", options=options)

    delay()

    driver.get(URL)
    delay()
except Exception as e:
    sys.exit(
        'update Chrome driver'
    )

g_recaptcha = driver.find_element_by_class_name('g-recaptcha')
outerIframe = g_recaptcha.find_element_by_tag_name('iframe')
outerIframe.click()

delay()

iframes = driver.find_elements_by_tag_name('iframe')
print(type(iframes))
audioBtnFound = False
audioBtnIndex = -1

for index in range(len(iframes)):
    driver.switch_to.default_content()
    iframe = driver.find_elements_by_tag_name('iframe')[index]
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(delayTime)
    try:
        audioBtn = driver.find_element_by_id('recaptcha-audio-button')
        audioBtn.click()
        audioBtnFound = True
        audioBtnIndex = index
        break
    except Exception as e:
        pass

if audioBtnFound:
    try:
        while True:
            src = driver.find_element_by_id('audio-source').get_attribute("src")
            print("[INFO] Audio src: %s" % src)

            urllib.request.urlretrieve(src, os.getcwd() + audioFile)
            key = audioToText(os.getcwd() + audioFile)
            print("[INFO] Recaptcha Key : %s" % key)

            driver.switch_to.default_content()
            iframe = driver.find_element_by_tag_name('iframe')[audioBtnIndex]
            driver.switch_to.frame(iframe)

            inputFields = driver.find_element_by_id('audio-response')
            inputFields.send_keys(key)
            delay()
            inputFields.send_keys(Keys.ENTER)
            delay()

            err = driver.find_element_by_class_name('rc-audiochallenge-error-message')[0]
            if err.text == "" or err.value_of_css_property('display') == 'none':
                print("[INFO] Succes!")
                break

    except Exception as e:
        print(e)
        sys.exit("[INFO] use proxy on the method")
else:
    sys.exit("[INFO] Audio Play Button not found! In vary rare cases!")