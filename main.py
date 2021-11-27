import pyrebase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
from config import firebaseConfig
import aiogram.utils.markdown as fmt
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
        openPage(user, user_id)
        



def parseMessages(driver, user_id):
    try:
        messages = ""
        messages =WebDriverWait(driver, 1).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, '[style="text-align: left; font: normal 0.9em verdana; cursor: pointer;"]'))).find_elements(By.TAG_NAME, 'tr')          
    except TimeoutException:
        print(user_id)
        return
    else:
        for mes in messages:
            td = mes.find_elements(By.TAG_NAME, "td")
            if "show" in mes.get_attribute("id"): pass
            if len(td)<5: pass
            else:
                if td[0].text=="":  pass
                else:
                    time.sleep(0.5)
                    try:
                        filesFromMes = td[2].find_elements(By.TAG_NAME, "a")
                    except StaleElementReferenceException:
                        print(user_id)
                    else:
                        fls = ""
                        for fil in filesFromMes:
                            fls+=fmt.hlink(url = fil.get_attribute("href"), title=fil.text + "\n")
                        date =  td[0].text 
                        theme = td[1].text 
                        teacher = td[3].text 
                        td[1].click()
                        idMes = mes.get_attribute("id")
                        try:
                            textMes = WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((By.ID, idMes.replace("tr", "show")))).find_element(By.TAG_NAME, 'span').text
                        except TimeoutException:
                            print(user_id)
                            return
                        td[1].click()
                        if theme=="": theme="--"
                        if teacher=="": teacher="--"
                        if fls=="": fls="--"
                        if textMes=="": textMes="--"
                        json = {"date": date, "theme": theme, "teacher": teacher, "files": fls, "textMessage": textMes}
                        if db.child("Messages").child(user_id).child(json["date"]).get().val() == json:   
                            pass
                            return
                            
                        else:   db.child("Messages").child(user_id).child(json["date"]).update(json)
                        


def openPage(user, user_id):
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
            parseMessages(driver, user_id)
            while True:
                try:
                    driver.find_element(By.LINK_TEXT, "Следующая").click()
                except NoSuchElementException:
                    driver.quit()
                    break
                else:
                    parseMessages(driver, user_id)
checkUsers()