import requests
from notificationz_sdk_python.models import *

class Notification:
    def __init__(self, api_url):
        self.api_url = api_url
        self.api_telegram_url = api_url + "telegram"
        self.api_email_url = api_url + "email"


    def send(self, destination: notification_destination, address, text, tag = None, source = None):
        # sends request to send notification container with details
        # subprocess.run(["pkill", "openvpn"])
        # print("killing vpn")
        # sleep(10)
        if destination == notification_destination.telegram:
            data = {"username": address, "message": text, "tag": tag, "source": source}    
            res = requests.post(self.api_telegram_url, json=data)
            print(res)
            return res

        if destination == notification_destination.email:
            pass
    