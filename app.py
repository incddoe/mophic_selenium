from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium.webdriver.chrome.options import Options
from configparser import ConfigParser

conf = ConfigParser()
conf.read("config.ini", encoding="utf8")

logins = conf._sections['credentials']
chrome_options = Options()
chrome_options.add_argument("--headless")

columns = ['ลำดับ',
 'ชื่อหน่วยให้บริการ',
 'ต้องติดตาม',
 'วันที่/เวลา ได้รับวัคซีน',
 'ชื่อ Vaccine',
 'เข็มที่',
 'Lot Number',
 'ผู้ผลิต',
 'ระยะเวลาถึงปัจจุบัน (วัน)',
 'จำนวนครั้งที่ติดตาม AEFI',
 'Serial No.',
 'วันหมดอายุ',
 'AEFI',
 'ชื่อผู้ให้',
 'ตำแหน่ง',
 'เลขที่ใบประกอบวิชาชีพ',
 'โทรศัพท์',
 'อาการ AEFI ที่พบ',
 'รหัสหน่วยให้บริการ',
 'ประเภท',
 'กลุ่ม'
 ]

def get_vaccine_records(name, logins):
    driver = webdriver.Chrome("./chromedriver.exe" )
    driver.get("https://cvp1.moph.go.th/dashboard")
    driver.find_element_by_id("O53_id-inputEl").send_keys(logins['department'])
    driver.find_element_by_id("O37_id-inputEl").send_keys(logins['user'])
    driver.find_element_by_id("O3F_id-inputEl").send_keys(logins['password'])

    dep_value = driver.find_element_by_id("O53_id-inputEl").get_attribute("value")
    user_value = driver.find_element_by_id("O37_id-inputEl").get_attribute("value")
    pwd_value = driver.find_element_by_id("O3F_id-inputEl").get_attribute("value")

    login_values = dict(
        department=dep_value,
        user=user_value,
        password=pwd_value
    )

    
    while login_values != logins:
        driver.find_element_by_id("O53_id-inputEl").clear()
        driver.find_element_by_id("O53_id-inputEl").send_keys(logins['department'])
        driver.find_element_by_id("O37_id-inputEl").clear()
        driver.find_element_by_id("O37_id-inputEl").send_keys(logins['user'])
        driver.find_element_by_id("O3F_id-inputEl").clear()
        driver.find_element_by_id("O3F_id-inputEl").send_keys(logins['password'])

        dep_value = driver.find_element_by_id("O53_id-inputEl").get_attribute("value")
        user_value = driver.find_element_by_id("O37_id-inputEl").get_attribute("value")
        pwd_value = driver.find_element_by_id("O3F_id-inputEl").get_attribute("value")

        login_values = dict(
            department=dep_value,
            user=user_value,
            password=pwd_value
        )

    

    login_bth = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "O6D_id")))
    login_bth.click()


    # menu vaccine
    #vaccine_menu = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "treeview-1013-record-3")))


    vaccine_menu = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[text()[contains(., 'Vaccine')]]")))
    action = ActionChains(driver)
    action.double_click(vaccine_menu).perform()

    # ทะเบียนกลุ่มเป้าหมาย
    #driver.find_element_by_id("treeview-1013-record-10").click()
    driver.find_element_by_xpath("//*[text()[contains(., 'ทะเบียนกลุ่มเป้าหมาย')]]").click()
    search_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "O206_id-inputEl")))
    search_box.send_keys(name)
    show_button = driver.find_element_by_id("O20A_id")
    show_button.click()
    
    try:
        #record = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gridview-1020 td")))
        #record_xpath = "//div[@role='dialog']/div/div/div/div/div/div/div/div[4]/div/div/div/div/div/div/div/div[@role='presentation']/div[2]/div/div/div/div/div/div/div/div/div/div[@role='grid']/div/div[@role='presentation']/div/div[@role='presentation' and @class='x-grid-item-container']/table/tbody/tr[1]"
        record_xpath = "//div[4]//div[@role='presentation' and @class='x-grid-item-container']/table[1]"
        record = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, record_xpath)))
    except:
        record = "Failed"

    if record == "Failed":
        driver.quit()
        return 0, None
        
    else:
        #print(record.get_attribute("innerHTML"))
        action = ActionChains(driver)
        action.double_click(record).perform()

        try:
            vaccine_records = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#O411_id table")))
            soups = [BeautifulSoup(vaccine_record.get_attribute("innerHTML"), "html.parser") for vaccine_record in vaccine_records]
            table = [[data.text for data in soup.findAll("td")] for soup in soups]
            df = pd.DataFrame(table, columns=columns)
            df['cid'] = name
        except: 
            df = pd.DataFrame([[None for i in range(len(columns))]], columns=columns)
            df['cid'] = name

        driver.quit()

        return 1, df


if __name__ == "__main__":
    from sys import argv
    name = argv[1]
    print(get_vaccine_records(name, logins))

