from typing import Final
from datetime import datetime
from time import sleep
import json
import os
import csv
import telebot
import threading
import requests
from lxml import html


login_file_path = os.path.join(os.path.dirname(__file__), "login.json")
login = json.load(open(login_file_path))
TOKEN: Final = login["token"]
BOT_USERNAME: Final = login["bot_username"]
EMAIL: Final = login["email"]
PASSWORD: Final = login["password"]

login = {
    'client_id' : 'nbgi_taiko',
    'redirect_uri': 'https://www.bandainamcoid.com/v2/oauth2/auth?back=v3&client_id=nbgi_taiko&scope=JpGroupAll&redirect_uri=https%3A%2F%2Fdonderhiroba.jp%2Flogin_process.php%3Finvite_code%3D%26abs_back_url%3D%26location_code%3D&text=',
    'login_id': EMAIL,
    'password': PASSWORD,
    'language': 'en',
    'cookie': '{}'
}
loginv2 = {
    'id_pos': 2,
    'mode': 'exec'
}
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}




bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(message.chat.id, "Hello! Please input your taikoban number to begin (I only track 10 stars for now >.<)")

@bot.message_handler(func=lambda message: True)
def start_scraping(message):
    #bot.send_message(message.chat.id, "Processing! will send csv when completed da-don! (est. 2-4 min)")
    threading.Thread(target=main_scraper, args=(message.text, message)).start()
        
def main_scraper(TAIKO_NO, message):
    print("login for " + TAIKO_NO)

    session = requests.Session()
    start = session.post('https://account-api.bandainamcoid.com/v3/login/idpw', data=login, headers=header)
    if "input_error" in json.loads(start.text):
        print("login failed for " + TAIKO_NO)
        bot.send_message(message.chat.id, "Timeout or login credentials incorrect")
        return
    redirect = json.loads(start.text)["redirect"]
    login_success = session.get(redirect, headers=header)
    get_into_dh = session.post('https://donderhiroba.jp/login_select.php', data=loginv2, headers=header)
    print("login completed for " + TAIKO_NO)

    
    name = ""
    if(TAIKO_NO != ""):
        user_page = session.get('https://donderhiroba.jp/user_profile.php?taiko_no={}'.format(TAIKO_NO), headers=header)
        user_tree = html.fromstring(user_page.content)
        
        user_get_name = user_tree.xpath('/html/body/div[1]/div/div[1]/div[1]/div[2]/text()') #get name if no dan is present
        if(user_get_name != []):
            name = user_get_name[2].strip()
            print(user_get_name)

        else:
            user_get_name = user_tree.xpath('/html/body/div[1]/div/div[1]/div[1]/div[2]/div[1]/text()') #get name if dan is present
            if(user_get_name != []):
                name = user_get_name[0].strip()
                print(name)

            else:
                user_get_name = user_tree.xpath('/html/body/div[1]/div/div[1]/div[1]/div/div[2]/text()') #get name if none cause its me :)
                if(user_get_name != []):
                    name = user_get_name[0].strip()
                    print(name)

                else:                                                                                   #no user exist
                    print("no user exist " + TAIKO_NO)
                    bot.send_message(message.chat.id, "No user exist for Taiko number")
                    return

    dict_info = []

    json_file_path = os.path.join(os.path.dirname(__file__), "10star_list.json")
    songlist = json.load(open(json_file_path, encoding="utf8"))

    #bot.send_message(message.chat.id, "Now getting J-pop section")
    for o in songlist:
        print("Started scraping {} for {}".format(o, TAIKO_NO))
        for i in songlist[o]:
            if(i["url"] != "nil"):
                score_page = session.get("https://donderhiroba.jp/score_detail.php{}&taiko_no={}".format(i["url"], TAIKO_NO), headers=header)
                score_tree = html.fromstring(score_page.content)

                played_check = score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[1]/span/text()')
                if(played_check != []):
                    crown_check = score_tree.xpath('/html/body/div[1]/div/div[2]/div[2]/img[2]/@src')
                    if(crown_check != []):
                        crown = getCrown(crown_check[0])
                    else:
                        crown = "None"

                    medal_check = score_tree.xpath('/html/body/div[1]/div/div[2]/div[2]/img[3]/@src')
                    if(medal_check != []):
                        medal = getMedal(medal_check[0])
                    else:
                        medal = "None"

                    score = int(score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[2]/span/text()')[0][:-1])
                    good  = int(score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[3]/span/text()')[0][:-1])
                    ok    = int(score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[5]/span/text()')[0][:-1])
                    bad   = int(score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[7]/span/text()')[0][:-1])
                    combo = int(score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[4]/span/text()')[0][:-1])
                    droll = int(score_tree.xpath('/html/body/div[1]/div/div[2]/div[3]/div[6]/span/text()')[0][:-1])
                    average = (good*100 + ok*50) / (good+ok+bad)

                    dict_info.append([i["name"], score, crown, medal, good, ok, bad, combo, droll, average])

                else:
                    dict_info.append([i["name"], 0, "None", "None", 0, 0, 0, 0, 0, 0])

            else:
                dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])

    #print("Started scraping kids for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Kids section")
    #for i in songlist["Kids"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])
#
    #print("Started scraping anime for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Anime section")
    #for i in songlist["Anime"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])
#
    #print("Started scraping vocaloid for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Vocaloid section")
    #for i in songlist["Vocaloid"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])
#
    #print("Started scraping gamemusic for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Game-Music section")
    #for i in songlist["Game Music"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])
#
    #print("Started scraping variety for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Variety section")
    #for i in songlist["Variety"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])
#
    #print("Started scraping classic for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Classical section")
    #for i in songlist["Classical"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])
#
    #print("Started scraping namco for " + TAIKO_NO)
    #bot.send_message(message.chat.id, "Now getting Namco-Original section")
    #for i in songlist["Namco Original"]:
    #    if(i["url"] != "nil"):
    #        driver.get("https://donderhiroba.jp/score_detail.php" + i["url"] + "&taiko_no=" + TAIKO_NO)
    #        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span")))
    #        
    #        try:
    #            crownlink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[2]").get_attribute("src")
    #            crown = getCrown(crownlink)
    #        except NoSuchElementException:
    #            crown = "None"
#
    #        try:
    #            medallink = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/img[3]").get_attribute("src")
    #            medal = getMedal(medallink)
    #        except NoSuchElementException:
    #            medal = "None"
    #        
    #        good = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text[:-1])
    #        ok = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text[:-1])
    #        bad = int(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text[:-1])
    #        average = (good*100 + ok*50) / (good+ok+bad)
    #        
    #        if(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text == "---位"):
    #            score = "0点"
    #        else:
    #            score = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/span").text
    #        
    #        dict_info.append([
    #            i["name"],
    #            score,
    #            crown,
    #            medal,
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[3]/span").text, #Good
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[5]/span").text, #Ok
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[7]/span").text, #Miss
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[4]/span").text, #Combo
    #            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[6]/span").text, #Drumroll
    #            average
    #            ])
    #    else:
    #        #print("no_url")
    #        dict_info.append([i["name"], "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil", "nil"])



    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    title = ["Donder: {}     Taikoban: {}     Generated on: {}".format(name, TAIKO_NO, dt_string)]

    dict_header = ["name", "score", "crown", "medal", "good", "ok", "miss", "maxcombo", "drumroll", "accuracy"]

    crownless = 0
    passed = 0
    fc = 0
    dfc = 0

    white = 0
    bronze = 0
    silver = 0
    gold = 0
    pink = 0
    purple = 0
    kiwami = 0

    totalaverage = 0
    totalattempt = 0

    final = []
    final.append(title)
    final.append(["----"])
    final.append(dict_header)
    for i in dict_info:
        if i in final:
            continue
        else:
            if(i[2] == "Crownless"):
                crownless += 1
            elif(i[2] == "Pass"):
                passed += 1
            elif(i[2] == "FC"):
                fc += 1
            elif(i[2] == "DFC"):
                dfc += 1

            if(i[3] == "White"):
                white += 1
            elif(i[3] == "Bronze"):
                bronze += 1
            elif(i[3] == "Silver"):
                silver += 1
            elif(i[3] == "Gold"):
                gold += 1
            elif(i[3] == "Pink"):
                pink += 1
            elif(i[3] == "Purple"):
                purple += 1
            elif(i[3] == "Kiwami"):
                kiwami += 1

            if(i[9] != "nil" and i[1] != "0点"):
                totalattempt += 1
                totalaverage += i[9]

            final.append(i)
    final.append(["----"])
    final.append(["----"])
    final.append(["Crownless: {}".format(str(crownless)), "Pass: {}".format(str(passed)), "FC: {}".format(str(fc)), "DFC: {}".format(str(dfc))])
    final.append(["White: {}".format(str(white)), "Bronze: {}".format(str(bronze)), "Silver: {}".format(str(silver)), "Gold: {}".format(str(gold)), "Pink: {}".format(str(pink)), "Purple: {}".format(str(purple)), "Kiwami: {}".format(str(kiwami)),])
    final.append(["Overall accuracy: {}".format(str(totalaverage/totalattempt)),])
    final.append(["Accuracy calculated by:", "Good=100%", "Ok=50%", "Bad=0%"])

    csv_file_path = os.path.join(os.path.dirname(__file__), "Scorelist{}.csv".format(TAIKO_NO))
    with open(csv_file_path, 'w', encoding="utf8", newline="") as csv_file:  
        writer = csv.writer(csv_file, delimiter=',' )
        writer.writerows(final)
    
    csv_file = open(csv_file_path, 'r', encoding="utf8")
    print("sent file for " + TAIKO_NO)
    bot.send_message(message.chat.id, "Done! file has been sent!")
    bot.send_document(message.chat.id, csv_file)
    csv_file.close()
    os.remove(csv_file_path)

def getCrown(link):
    if(link == "image/sp/640/crown_large_0_640.png"):
        return "Crownless"
    if(link == "image/sp/640/crown_large_1_640.png"):
        return "Pass"
    if(link == "image/sp/640/crown_large_2_640.png"):
        return "FC"
    if(link == "image/sp/640/crown_large_4_640.png"):
        return "DFC"
    
def getMedal(link):
    if(link == "image/sp/640/best_score_rank_2_640.png"):
        return "White"
    if(link == "image/sp/640/best_score_rank_3_640.png"):
        return "Bronze"
    if(link == "image/sp/640/best_score_rank_4_640.png"):
        return "Silver"
    if(link == "image/sp/640/best_score_rank_5_640.png"):
        return "Gold"
    if(link == "image/sp/640/best_score_rank_6_640.png"):
        return "Pink"
    if(link == "image/sp/640/best_score_rank_7_640.png"):
        return "Purple"
    if(link == "image/sp/640/best_score_rank_8_640.png"):
        return "Kiwami"
    


bot.infinity_polling()