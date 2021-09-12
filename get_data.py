# -*- coding: utf-8 -*-
# chrome version : 93.0

import datetime
import pytz
from selenium.webdriver.chrome.webdriver import WebDriver
now_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

import time
import os
import re
from os import path
OWN_FILE_NAME = path.splitext(path.basename(__file__))[0]
RACR_HTML_DIR = "race_html"


import logging
logger = logging.getLogger(__name__) #ファイルの名前を渡す

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "https://regist.netkeiba.com/account/?pid=login"
DATA_URL = "https://db.netkeiba.com/?pid=race_search_detail"
WAIT_SECOND = 5

def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def get_race_html():
    # 去年までのデータ
    for year in range(2020, now_datetime.year):
        for month in range(1, 13):
            get_race_html_by_year_and_month(year,month)
    # 今年のデータ
    for year in range(now_datetime.year, now_datetime.year+1):
        for month in range(1, now_datetime.month+1):
            get_race_html_by_year_and_month(year,month)

def get_race_html_by_year_and_month(year, month):
    options= ChromeOptions()
    driver = Chrome(executable_path=r'chromedriver.exe',options=options)

    wait = WebDriverWait(driver, 10)
    driver.get(LOGIN_URL)
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # メールアドレスとパスワードの設定
    USER = "takagakiryu@gmail.com"
    PASS = "Rt4719380"

    # ログインフォームを取得
    login_form = driver.find_element_by_class_name("member__loginBox")

    # ログインフォーム内のid,pass入力部分を取得
    login_id = login_form.find_element_by_name("login_id")
    login_pass = login_form.find_element_by_name("pswd")

    # ログインid,passの入力
    login_id.send_keys(USER)
    login_pass.send_keys(PASS)

    # ログインボタン要素を取得し、フォームを送信する
    login_button = login_form.find_element_by_css_selector("input")
    login_button.submit()
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # レース詳細検索URLにアクセス
    wait = WebDriverWait(driver,10)
    driver.get(DATA_URL)
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    # 期間を選択
    start_year_element = driver.find_element_by_name('start_year')
    start_year_select = Select(start_year_element)
    start_year_select.select_by_value(str(year))
    start_mon_element = driver.find_element_by_name('start_mon')
    start_mon_select = Select(start_mon_element)
    start_mon_select.select_by_value(str(month))
    end_year_element = driver.find_element_by_name('end_year')
    end_year_select = Select(end_year_element)
    end_year_select.select_by_value(str(year))
    end_mon_element = driver.find_element_by_name('end_mon')
    end_mon_select = Select(end_mon_element)
    end_mon_select.select_by_value(str(month))

    # 競馬場をチェック
    for i in range(1,11):
        terms = driver.find_element_by_id("check_Jyo_"+ str(i).zfill(2))
        terms.click()

    # 表示件数を選択(20,50,100の中から最大の100へ)
    list_element = driver.find_element_by_name('list')
    list_select = Select(list_element)
    list_select.select_by_value("100")

    # フォームを送信
    frm = driver.find_element_by_css_selector("#db_search_detail_form > form")
    frm.submit()
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)

    """"
    検索結果ページの検索数とファイル数を比較する
    """
    
    # 検索結果を保存するフォルダがなかったら作る
    save_dir = RACR_HTML_DIR+"/"+str(year)+"/"+str(month)   # 検索結果を保存するフォルダ
    if not os.path.isfile(save_dir):
        makedirs(save_dir)
        logging.info("make new data folder")

    # 保存フォルダ内のファイルを検索
    saved_files = os.listdir(save_dir)  # 保存ファイル名をリストで取得
    saved_files_num = len(saved_files)  # 保存ファイルの数

    # 検索結果数を取得
    total_num_and_now_num = driver.find_element_by_xpath("//*[@id='contents_liquid']/div[1]/div[2]").text
    total_num = int(re.search(r'(.*)件中', total_num_and_now_num).group().strip("件中")) 


    while saved_files_num != total_num:    # 検索結果とファイル数が一致したなら、次の年月        
        # 検索結果ページ内の全レースを取得し、ファイルがあるか確認
        time.sleep(1)
        wait.until(EC.presence_of_all_elements_located)
        all_rows = driver.find_element_by_class_name("race_table_01").find_elements_by_tag_name("tr")
        for row in range(1,len(all_rows)):

            all_rows = driver.find_element_by_class_name("race_table_01").find_elements_by_tag_name("tr")
            url = all_rows[row].find_elements_by_tag_name("td")[4].find_element_by_tag_name("a")
            url_attribute = url.get_attribute("href")
            url_list = url_attribute.split("/")
            race_id = url_list[-2]
            save_file_path = race_id + ".html"  # 保存するファイル名

            if save_file_path in saved_files:
                print(save_file_path in saved_files)   # ファイルが既にあるか確認
            else:
                print(save_file_path in saved_files)

                all_rows = driver.find_element_by_class_name("race_table_01").find_elements_by_tag_name("tr")
                url = all_rows[row].find_elements_by_tag_name("td")[4].find_element_by_tag_name("a")
                url_attribute = url.get_attribute("href")
                url_list = url_attribute.split("/")
                race_id = url_list[-2]
                save_file_path = race_id + ".html"  # 保存するファイル名
                    
                # 別ウインドウを開く
                driver.execute_script('window.open()')
                driver.switch_to.window(driver.window_handles[1])
                driver.get(url_attribute)
                time.sleep(1)
                wait.until(EC.presence_of_all_elements_located)
                    
                response = driver.page_source
                time.sleep(1)
                wait.until(EC.presence_of_all_elements_located)

                save_file_path = save_dir + "/" + race_id + ".html"

                with open(save_file_path, "w", encoding = "utf-8") as file:
                    file.write(response)
                print(save_file_path)
                # 別ウィンドウを閉じる。
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        try:
            target = driver.find_elements_by_link_text("次")[0]
            driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
        except IndexError:
            break
    
    driver.close()