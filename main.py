import pyrebase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
from config import firebaseConfig
firebase = pyrebase.initialize_app(firebaseConfig)
db= firebase.database()

s=Service(ChromeDriverManager().install())
url = 'https://lk.sut.ru/cabinet/'
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

def checkUsers():
    users = db.child("Users").get().each()
    for user in users:
        user_id = user.key()
        user = db.child("Users").child(user_id).get().val()
        openPage(user)
        

def parseFiles(user, driver):
            try:
                time.sleep(1)
                table = ""
                table =  WebDriverWait(driver, 1).until(
    EC.visibility_of_element_located((By.XPATH, '//*[@id="mytable"]/tbody'))).find_elements(By.TAG_NAME, "tr")
            except Exception as e:
                print(e)
                pass
            finally: 
                for row in table:
                    time.sleep(1)
                    file = row.find_elements(By.TAG_NAME, "td")
                    if len(file)>3 and file[2].text != "":
                        fileName = file[2].find_element(By.TAG_NAME, "a").get_attribute("href")
                        db.child("Files").child(file[3].text).child(file[1].text.replace(".", "").replace("[", "").replace("]", "")).update({user["login"].replace(".", ""): str(fileName)})

def openPage(user):
    print(user["login"])
    driver = webdriver.Chrome(service = s, options = chrome_options)
    driver.get(url)
    try:
        login = ""
        login = WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((By.NAME, "users")))
    except Exception as e:
        print(e)
        pass
    finally:
        login.send_keys(user["login"])
        driver.find_element(By.NAME,"parole").send_keys(user["password"])
        driver.find_element(By.NAME, "logButton").click()
        try:
            messages = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.ID, "menu_li_840")))
        except Exception as e:
            print(e)
            pass
        finally:   
            messages.click()
            try:
                mesin = ""
                mesin = WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "mesin")))
            except Exception as e:
                print(e)
                pass
            finally: 
                mesin.click()
                parseFiles(user, driver)
                while True:
                    try:
                        driver.find_element(By.LINK_TEXT, "Следующая").click()
                    except NoSuchElementException:
                        driver.quit()
                        break
                    else:
                        parseFiles(user, driver)

checkUsers()