import requests
from .models import *

class Notification:
    def __init__(self, api_url):
        self.api_url = api_url
        self.api_telegram_url = api_url + "telegram"
        self.api_email_url = api_url + "email"


    def send(self, destination: notification_destinations, address, text, tag = None, source = None):
        # sends request to send notification container with details
        # subprocess.run(["pkill", "openvpn"])
        # print("killing vpn")
        # sleep(10)
        if destination not in notification_destinations:
            raise Exception(f"destination not in 'models.notification_destinations'.")

        if destination == notification_destinations.telegram.value or destination == notification_destinations.telegram:
            print("start")
            data = {"username": address, "message": text, "tag": tag, "source": source}    
            res = requests.post(self.api_telegram_url, json=data)
            # print(res)
            
            return res

        if destination == notification_destinations.email.value or destination == notification_destinations.email:
            pass
    