from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from time import sleep
from alive_progress import alive_bar
import json
import os
import csv
import subprocess
import sys

login_file_path = os.path.join(os.path.dirname(__file__), "login.json")
login = json.load(open(login_file_path, encoding="utf8"))
EMAIL = login["email"]
PASSWORD = login["password"]
TAIKO_NO = login["taiko_no"]
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    with alive_bar(monitor=None, stats=None, title="Login to DH.jp"):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get('https://account.bandainamcoid.com/login.html?client_id=nbgi_taiko&customize_id=&redirect_uri=https%3A%2F%2Fwww.bandainamcoid.com%2Fv2%2Foauth2%2Fauth%3Fback%3Dv3%26client_id%3Dnbgi_taiko%26scope%3DJpGroupAll%26redirect_uri%3Dhttps%253A%252F%252Fdonderhiroba.jp%252Flogin_process.php%253Finvite_code%253D%2526abs_back_url%253D%2526location_code%253D%26text%3D&prompt=login')
        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.ID, "mail")))
        WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.ID, "mail")))
        sleep(1)
        driver.find_element(By.ID, "mail").send_keys(EMAIL)
        driver.find_element(By.ID, "pass").send_keys(PASSWORD + Keys.ENTER)

        try:
            WebDriverWait(driver, timeout=3).until(EC.url_changes("https://donderhiroba.jp/login_select.php"))
            WebDriverWait(driver, timeout=12).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/ul/li[3]/div/div[6]/form/div/a")))
            WebDriverWait(driver, timeout=3).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        except TimeoutException:
            print("Timeout or login credentials incorrect")
            driver.quit()
            exit()
            
        #print("wait done")
        sleep(1)
        driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        #print("Sleeping for 1 second")
        sleep(1)
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/ul/li[3]/div/div[6]/form/div/a").click()
        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.ID, "mydon_area")))
        if(TAIKO_NO != ""):
            driver.get('https://donderhiroba.jp/user_profile.php?taiko_no=' + TAIKO_NO)
            try:
                driver.find_element(By.XPATH, "/html/body/div[1]/div/div/table/tbody/tr/td[2]")
                print("No user exist for Taiko number")
                driver.quit()
                exit()
            except NoSuchElementException:
                pass

    dict_header = ["name", "score", "good", "ok", "miss", "maxcombo", "drumroll"]
    dict_info = []

    json_file_path = os.path.join(os.path.dirname(__file__), "10star_list.json")
    songlist = json.load(open(json_file_path, encoding="utf8"))

    with alive_bar(len(songlist["J-pop"])) as bar:
        bar.title("J-pop         ")
        for i in songlist["J-pop"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Kids"])) as bar:
        bar.title("Kids          ")
        for i in songlist["Kids"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Anime"])) as bar:
        bar.title("Anime         ")
        for i in songlist["Anime"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Vocaloid"])) as bar:
        bar.title("Vocaloid      ")
        for i in songlist["Vocaloid"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Game Music"])) as bar:
        bar.title("Game Music    ")
        for i in songlist["Game Music"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Variety"])) as bar:
        bar.title("Variety       ")
        for i in songlist["Variety"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Classical"])) as bar:
        bar.title("Classical     ")
        for i in songlist["Classical"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()

    with alive_bar(len(songlist["Namco Original"])) as bar:
        bar.title("Namco Original")
        for i in songlist["Namco Original"]:
            if(i["url"] != "nil"):
                driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
                #print(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text)
                dict_info.append([
                    i["name"],
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text, #Score
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
                    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text #Drumroll
                    ])
            else:
                #print("no_url")
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil"])
            bar()


    with alive_bar(monitor=None, stats=None, title="Cleaning list "):
        driver.quit()
        final = []
        final.append(dict_header)
        for i in dict_info:
            if i in final:
                continue
            else:
                final.append(i)

    with alive_bar(monitor=None, stats=None, title="Writing csv   "):
        csv_file_path = os.path.join(os.path.dirname(__file__), "Scorelist.csv")
        with open(csv_file_path, 'w', encoding="utf8", newline="") as csv_file:  
            writer = csv.writer(csv_file, delimiter=',' )
            writer.writerows(final)
        

if __name__ == "__main__":
    main()