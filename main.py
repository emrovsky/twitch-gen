import base64
import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

import random_strings

import curl_cffi.requests
import requests
from random_username.generate import generate_username
import modules.kasada
import modules.tempmail
import logging
import sys
import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)



class NegroFormatter(logging.Formatter):
    COLORS = {
        'DBG': '\033[94m',
        'INF': '\033[0m',
        'WAR': '\033[93m',
        'ERR': '\033[91m',
        'SUC': '\033[92m'
    }
    RESET = '\033[0m'

    def format(self, record):
        levelname_short = {
            'DEBUG': 'DBG',
            'INFO': 'INF',
            'WARNING': 'WAR',
            'ERROR': 'ERR',
            'SUCCESS': 'SUC'
        }.get(record.levelname, record.levelname[:3].upper())
        log_color = self.COLORS.get(levelname_short, self.RESET)
        timestamp = self.formatTime(record, "%H:%M:%S")
        log_message = super().format(record)
        return f"{log_color}[{timestamp}] {log_color}{levelname_short:<3}{self.RESET}: {log_message}"

    def formatMessage(self, record):
        levelname_short = {
            'DEBUG': '🛠️',
            'INFO': '📢',
            'WARNING': '⚠️',
            'ERROR': '⛔',
            'SUCCESS': '✅'
        }.get(record.levelname, record.levelname[:3].upper())
        return f"{levelname_short} {super().formatMessage(record)}"

class NegroLogger:
    SUCCESS = 25

    def __init__(self, name='FancyLogger', level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self._configure_logger()

    def _configure_logger(self):
        handler = logging.StreamHandler(sys.stdout)
        formatter = NegroFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        logging.addLevelName(self.SUCCESS, 'SUCCESS')
        setattr(self.logger, 'success', lambda message, *args, **kwargs: self.logger.log(self.SUCCESS, message, *args, **kwargs))

    def get_logger(self):
        return self.logger

negrologger = NegroLogger().get_logger()
class Gen:
    def __init__(self):
        self.session = curl_cffi.requests.Session()

        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
            'Client-Session-ID': '771f15afb0d617c5',
            'Client-Version': 'ae95a7ae-af69-4748-bbd3-39445dc7cae3',
            'Connection': 'keep-alive',
            'Origin': 'https://www.twitch.tv',
            'Pragma': 'no-cache',
            'Referer': 'https://www.twitch.tv/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'X-Auth-Action': 'register',
            'X-Device-ID': random_strings.random_string(32),
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
        self.session.proxies = {'http': 'http://' + self.proxy.strip(), 'https': 'http://' + self.proxy.strip()}

        self.nickname = generate_username(1)[0] + str(random.randint(100, 999))
        self.password = random_strings.random_string(10)+random.choice(['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=']) + str(random.randint(10, 99))
        self.emailapi = modules.tempmail.Mail(self.proxy)

        while True:
            self.email = self.emailapi.email
            self.email_token = self.emailapi.mailtoken
            if self.email != None:
                break



        negrologger.info(f"Creating account with mail: {self.email}")

    def set_fake_social_media(self):
        social_medias = []
        for social_media in config["social_media"]:
            if config["social_media"][social_media]:
                social_medias.append(social_media)
        added_social_medias = []
        for social_media in social_medias:
            data = json.dumps([
               {
                  "operationName":"CreateSocialMedia",
                  "variables":{
                     "input":{
                        "url":f"http://{social_media}.com/{self.nickname}",
                        "title":str(social_media),
                        "channelID":str(self.userID)
                     }
                  },
                  "extensions":{
                     "persistedQuery":{
                        "version":1,
                        "sha256Hash":"797eca582ffcc52e2f773f5c81277490eeab2989dc12e084d932eb291498f309"
                     }
                  }
               }
            ])
            response = self.session.post('https://gql.twitch.tv/gql', data=data, verify=False)
            if response.status_code == 200:
                added_social_medias.append(social_media)
        return added_social_medias
    def set_bio(self):
        data = json.dumps([
           {
              "operationName":"UpdateUserProfile",
              "variables":{
                 "input":{
                    "displayName":self.nickname,
                    "description":random.choice(open("bio.txt", "r",encoding="utf-8").readlines()).strip(),
                    "userID":str(self.userID)
                 }
              },
              "extensions":{
                 "persistedQuery":{
                    "version":1,
                    "sha256Hash":"991718a69ef28e681c33f7e1b26cf4a33a2a100d0c7cf26fbff4e2c0a26d15f2"
                 }
              }
           }
        ])

        response = self.session.post('https://gql.twitch.tv/gql', data=data, verify=False)
        if response.status_code == 200:
            return True
        else:
            return False
    def upload_pfp(self):

        data = json.dumps(
            [
                {
                    "operationName": "EditProfile_CreateProfileImageUploadURL",
                    "variables": {
                        "input": {
                            "userID": self.userID,
                            "format": "PNG"
                        }
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "e1b65d20f16065b982873da89e56d9b181f56ba6047d2f0e458579c4033fba01"
                        }
                    }
                }
            ]
        )

        response = self.session.post('https://gql.twitch.tv/gql', data=data, verify=False)
        upload_url = response.json()[0]["data"]["createProfileImageUploadURL"]["uploadURL"]

        headers = {
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'origin': 'https://www.twitch.tv',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.twitch.tv/',
            'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
        }
        profile_photo_to_upload_ = random.choice(os.listdir(os.path.join(os.path.dirname(__file__), 'profile_photos')))

        profile_photo_to_upload_path = os.path.join(os.path.dirname(__file__), 'profile_photos',
                                                    profile_photo_to_upload_)
        with open(profile_photo_to_upload_path, 'rb') as f:
            data = f.read()

        response = requests.put(
            upload_url,
            headers=headers,
            data=data,
            proxies=self.session.proxies

        )

        if response.status_code == 200:
            return profile_photo_to_upload_
        else:
            return False
    def upload_banner(self):

        data = json.dumps([
           {
              "operationName":"EditProfile_CreateProfileBannerImageUploadURL",
              "variables":{
                 "input":{
                    "userID":str(self.userID),
                    "format":"PNG"
                 }
              },
              "extensions":{
                 "persistedQuery":{
                    "version":1,
                    "sha256Hash":"bd016b5e4a54fa813ef0d1cee89532dae14845dbc0243a4aa5011649fb968c0b"
                 }
              }
           }
        ])
        response = self.session.post('https://gql.twitch.tv/gql', data=data)
        upload_url = response.json()[0]["data"]["createProfileBannerImageUploadURL"]["uploadURL"]

        headers = {
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'origin': 'https://www.twitch.tv',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.twitch.tv/',
            'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
        }
        banner_photo_to_upload_ = random.choice(os.listdir(os.path.join(os.path.dirname(__file__), 'banner_photos')))
        banner_photo_to_upload_path = os.path.join(os.path.dirname(__file__), 'banner_photos',
                                                    banner_photo_to_upload_)
        with open(banner_photo_to_upload_path, 'rb') as f:
            data = f.read()

        response = requests.put(
            upload_url,
            headers=headers,
            data=data,
            proxies=self.session.proxies

        )

        data = json.dumps([
           {
              "operationName":"UpdateHeroPreset",
              "variables":{
                 "input":{
                    "channelID":str(self.userID),
                    "heroPreset":"PRESET_2"
                 }
              },
              "extensions":{
                 "persistedQuery":{
                    "version":1,
                    "sha256Hash":"4aca7f76bdf7ceaed5a5acf6513ff837f0faad647dc358d1fc62d9823de2a2ba"
                 }
              }
           }
        ])
        response = self.session.post('https://gql.twitch.tv/gql', data=data)

        if response.status_code == 200:
            return banner_photo_to_upload_
        else:
            return False
    def upload_video_player_banner(self):

        data = json.dumps([
           {
              "operationName":"EditProfile_CreateChannelOfflineImageUploadURL",
              "variables":{
                 "input":{
                    "userID":str(self.userID),
                    "format":"JPG"
                 }
              },
              "extensions":{
                 "persistedQuery":{
                    "version":1,
                    "sha256Hash":"0d3139de7fbc4ee14f1d07cace53a89c5d938405bedb1a3f316b0fec5d4c8a36"
                 }
              }
           }
        ])

        response = self.session.post('https://gql.twitch.tv/gql', data=data, verify=False)

        upload_url = response.json()[0]["data"]["createChannelOfflineImageUploadURL"]["uploadURL"]

        headers = {
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'origin': 'https://www.twitch.tv',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.twitch.tv/',
            'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
        }
        banner_photo_to_upload_ = random.choice(os.listdir(os.path.join(os.path.dirname(__file__), 'video_player_banners')))
        banner_photo_to_upload_path = os.path.join(os.path.dirname(__file__), 'video_player_banners',
                                                   banner_photo_to_upload_)
        with open(banner_photo_to_upload_path, 'rb') as f:
            data = f.read()

        response = requests.put(
            upload_url,
            headers=headers,
            data=data,
            proxies=self.session.proxies

        )


        if response.status_code == 200:
            return banner_photo_to_upload_
        else:
            return False
    def create(self):
        salamoonder_api = modules.kasada.salamoonder(api_key=config["salamoonder_api_key"])
        while True:
            try:
                task_id = salamoonder_api.createTask(
                    task_type="KasadaCaptchaSolver",
                    pjs_url="https://k.twitchcdn.net/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js",
                    cd_only="false"
                )

                solution = salamoonder_api.getTaskResult(config["salamoonder_api_key"], task_id)

                self.session.headers["x-kpsdk-cd"] = solution["x-kpsdk-cd"]
                self.session.headers["x-kpsdk-cr"] = solution["x-kpsdk-cr"]
                self.session.headers["x-kpsdk-r"] = solution["x-kpsdk-r"]
                self.session.headers["x-kpsdk-st"] = solution["x-kpsdk-cr"]
                self.session.headers["x-kpsdk-ct"] = solution["x-kpsdk-ct"]
                break
            except:
                negrologger.error("Error solving kasada, retrying...")
        negrologger.debug(f"Got kasada solution: {self.session.headers['x-kpsdk-ct'][:50]}...")

        response = self.session.post('https://passport.twitch.tv/integrity')


        self.session.headers['Content-Type'] =  'text/plain;charset=UTF-8'

        data = json.dumps(
            {"username": self.nickname, "password": self.password, "email": self.email,
             "birthday": {"day": random.randint(10,20), "month": random.randint(1,11), "year": random.randint(1990,2000)}, "client_id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
             "is_password_guide": "nist", "integrity_token": response.json()['token']})


        response = self.session.post('https://passport.twitch.tv/protected_register', data=data)

        try:
            self.userID = response.json()['userID']
            self.access_token = response.json()['access_token']
            negrologger.success(f"[{self.nickname}] Account created successfully")

        except:
            negrologger.error(f"Error creating account: {response.json()['error']}")
            return False
        try:
            self.session.headers['Authorization'] = f'OAuth {self.access_token}'
        except:
            pass

        # self.session.headers['x-kpsdk-cd'] = modules.KpsdkCd.KpsdkCdSolver().get_kpsdk_cd() #ill not share that just paste if u can find some articles about it lolololol easy af to reverse

        task_id = salamoonder_api.createTask(
            task_type="KasadaCaptchaSolver",
            pjs_url="https://k.twitchcdn.net/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js",
            cd_only="true"
        )
        solution = salamoonder_api.getTaskResult(config["salamoonder_api_key"], task_id)

        self.session.headers["x-kpsdk-cd"] = solution["x-kpsdk-cd"]



        response = self.session.post('https://gql.twitch.tv/integrity', verify=False)
        #print(response.text, response.status_code)
        negrologger.debug(f"[{self.nickname}] Got integrity token : {response.json()['token'][:50]}...")

        self.session.headers['client-integrity'] = response.json()['token']

        

        if config["account_settings"]["verify_email"]:
            code = self.emailapi.get_code()
            negrologger.success(f"[{self.nickname}] Got verification code: {code}")
            
            data = json.dumps(
                [
                    {
                        "extensions": {
                            "persistedQuery": {
                                "version": 1,
                                "sha256Hash": "05eba55c37ee4eff4dae260850dd6703d99cfde8b8ec99bc97a67e584ae9ec31"
                            }
                        },
                        "operationName": "ValidateVerificationCode",
                        "variables": {
                            "input": {
                                "code": code,
                                "key": str(self.userID),
                                "address": self.email
                            }
                        }
                    }
                ]
            )
    
            response = self.session.post('https://gql.twitch.tv/gql', data=data, verify=False)
            if response.status_code == 200:
                negrologger.success(f"[{self.nickname}] Verified email")
            else:
                negrologger.error(f"[{self.nickname}] Error verifying email")




    def humanize_account(self):

        if config["humanize_account"]["avatar"]:
            uploaded_pfp =  self.upload_pfp()
        else:
            uploaded_pfp = None

        if config["humanize_account"]["banner"]:
            uploaded_banner = self.upload_banner()
        else:
            uploaded_banner = None

        if config["humanize_account"]["video_player_banner"]:
            uploaded_video_player_banner = self.upload_video_player_banner()
        else:
            uploaded_video_player_banner = None

        negrologger.info(f"[{self.nickname}] pfp: {uploaded_pfp}, banner: {uploaded_banner}, video_player_banner: {uploaded_video_player_banner}")

        if config["humanize_account"]["bio"]:
            upload_bio = self.set_bio()
        else:
            upload_bio = False

        if config["social_media"] !=  None:
            added_social_medias = self.set_fake_social_media()
        else:
            added_social_medias = []

        negrologger.info(f"[{self.nickname}] bio: {upload_bio}, social medias: {added_social_medias}")

        open("accounts.txt", "a").write(f"{self.nickname}:{self.password}:{self.access_token}\n")

total_generate_count = input("Enter total accounts to create> ")

        
def generate():
    try:
        gen = Gen()
        x = gen.create()
        if x != False:
            gen.humanize_account()
    except Exception as e:
        negrologger.error(f"Error generating account: {e}")


def main():


    with ThreadPoolExecutor(max_workers=config['threads']) as executor:
        for i in range(int(total_generate_count)):
            executor.submit(generate)


if __name__ == "__main__":
    main()