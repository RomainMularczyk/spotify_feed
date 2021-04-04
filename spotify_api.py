import random
import time
import requests
import urllib
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------ API endpoints ------------
api_endpoints = {
    "api_auth": "https://accounts.spotify.com/authorize"
}


def build_api_options(file):

    with open(file) as logs:
        log_id, log_pwd = logs.read().split("\n")
        
    api_auth_options = {
        "client_id": log_id,
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:5500",
        "show_dialog": "true",
        "scope": "user-library-read"
    }

    return urllib.parse.urlencode(api_auth_options)


def login_user(url, file):

    xpath_id = '//*[@id="login-username"]'
    xpath_pwd = '//*[@id="login-password"]'
    xpath_btn_login = '//*[@id="login-button"]'
    xpath_btn_accept = '//*[@id="auth-accept"]'

    with open(file) as logs:
        user_id, user_pwd = logs.read().split("\n")

    driver = uc.Chrome()
    driver.get(url)
    
    # Locate elements
    id_form = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath_id))
    )
    pwd_form = driver.find_element(By.XPATH, xpath_pwd)
    btn_log = driver.find_element(By.XPATH, xpath_btn_login)

    # Simulate human completing forms
    for letter in user_id:
        id_form.send_keys(letter)
        time.sleep(random.uniform(0.08, 0.2))
    for letter in user_pwd:
        pwd_form.send_keys(letter)
        time.sleep(random.uniform(0.05, 0.2))
    time.sleep(1)
    btn_log.click()

    # Locate accept API use button
    btn_accept = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath_btn_accept))
    )
    btn_accept.click()
    _, auth_token = driver.current_url.split("=")
    
    return auth_token


    

url = api_endpoints["api_auth"] + "?" + build_api_options("logs.txt")
print(login_user(url, "user_logs.txt"))