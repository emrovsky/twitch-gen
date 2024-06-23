import re

import tls_client
import time


class Mail:
    def __init__(self, proxy)-> None:
        self.session = tls_client.Session(client_identifier="chrome_120",random_tls_extension_order=True)
        self.session.proxies = {'http': 'http://' + proxy.strip(), 'https': 'http://' + proxy.strip()}
        self.session.headers = {
                'accept': '*/*',
                'cache-control': 'no-cache',
                'origin': 'https://temp-mail.org',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://temp-mail.org/',
                'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }

        self.email , self.mailtoken  = self.get_email()

    def get_twitter_verification_code(self, text):
        pattern = r'\b(\d{6})\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None

    def get_email(self):
        try:
            while True:
                try:
                    response = self.session.post('https://web2.temp-mail.org/mailbox')
                    break
                except Exception as e:
                    continue
            mailtoken = response.json()['token']
            email = response.json()['mailbox']
            self.session.headers['Authorization'] = f'Bearer {mailtoken}'
            return email , mailtoken
        except Exception as e:

            return None , None

    def get_code(self) -> int:
        tried = 0
        while True:

            try:
                response = self.session.get('https://web2.temp-mail.org/messages')
            except :
                continue


            if response.json()['messages'] != []:
                for message in response.json()['messages']:
                    if message['from'] == 'Twitch <no-reply@twitch.tv>':
                        return self.get_twitter_verification_code(message['subject'])
                break
            time.sleep(2)
            tried += 1
            if tried == 7:
                return False
