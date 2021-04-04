import random
import time
import requests
import urllib
import base64
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Spotify:

    def __init__(self, account_logs_file, api_logs_file, scope="user-library-read"):
        # ------------ API endpoints ------------
        self.api_endpoints = {
            "auth": "https://accounts.spotify.com/authorize",
            "token": "https://accounts.spotify.com/api/token",
            "saved_albums": "https://api.spotify.com/v1/me/albums"
        }

        # ------------ Loading logs ------------
        with open(account_logs_file) as account_logs:
            account_id, account_pwd = account_logs.read().split("\n")
        with open(api_logs_file) as api_logs:
            user_id, user_secret = api_logs.read().split("\n")

        # ------------ Logs ------------
        self.logs = {
            "account_id": account_id,
            "account_pwd": account_pwd,
            "user_id": user_id,
            "user_secret": user_secret
        }

        # ------------ Tokens ------------
        self.tokens = {
            "code": "",
            "access": "",
            "refresh": ""
        }

        # ------------ HTTP requests options ------------
        self.http_options = {
            "response_type": "code",
            "grant_type": "authorization_code",
            "code": self.tokens["code"],
            "redirect_uri": "http://127.0.0.1:5500",
            "scope": scope,
            "client_id": self.logs["user_id"],
            "client_secret": self.logs["user_secret"]
        }


    def login_user(self, webdriver):

        xpath = {
            "id": '//*[@id="login-username"]',
            "pwd": '//*[@id="login-password"]',
            "btn_login": '//*[@id="login-button"]',
            "btn_accept": '//*[@id="auth-accept"]'
        }

        api_auth_options = {
            "client_id": self.logs["user_id"],
            "response_type": "code",
            "redirect_uri": "http://127.0.0.1:5500",
            "show_dialog": "true",
            "scope": "user-library-read"
        }

        # --- Open webdriver ---
        driver = webdriver.Chrome()
        driver.get(self.api_endpoints["auth"] + "?" + urllib.parse.urlencode(api_auth_options))

        # --- Locate elements ---
        id_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath["id"]))
        )
        pwd_form = driver.find_element(By.XPATH, xpath["pwd"])
        btn_log = driver.find_element(By.XPATH, xpath["btn_login"])

        # --- Simulate human completing forms ---
        for letter in self.logs["account_id"]:
            id_form.send_keys(letter)
            time.sleep(random.uniform(0.08, 0.2))
        for letter in self.logs["account_pwd"]:
            pwd_form.send_keys(letter)
            time.sleep(random.uniform(0.05, 0.2))
        time.sleep(1)
        btn_log.click()

        # --- Locate accept API use button ---
        btn_accept = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath["btn_accept"]))
        )
        btn_accept.click()
        _, code = driver.current_url.split("=")
        
        self.tokens["code"] = code


    def get_access_token(self):

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        api_token_options = {
            "grant_type": "authorization_code",
            "code": self.tokens["code"],
            "redirect_uri": "http://127.0.0.1:5500",
            "client_id": self.logs["user_id"],
            "client_secret": self.logs["user_secret"]
        }

        r = requests.post(self.api_endpoints["token"] + "?" + urllib.parse.urlencode(api_token_options), headers=headers)
        access_token, refresh_token = r.json()["access_token"], r.json()["refresh_token"]

        self.tokens["access"] = access_token
        self.tokens["refresh"] = refresh_token

    
    def get_new_albums(self):

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + str(self.tokens["access"])
        }
        
        r = requests.get(self.api_endpoints["saved_albums"], headers=headers)
        response = r.json()["items"]

        data = []
        for obj in response:
            data.append({
                "artist": obj["album"]["artists"][0]["name"],
                "album": obj["album"]["name"]
            })

        return data


spotify = Spotify(account_logs_file="logs/user_logs.txt", api_logs_file="logs/logs.txt")
spotify.login_user(uc)
spotify.get_access_token()
print(spotify.get_new_albums())