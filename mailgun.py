import requests
from config import Config


def send_simple_msg():
        return requests.post(
            "https://api.mailgun.net/v3/sandboxa4c7fef9ea7e4617bb084b71bfb532a9.mailgun.org/messages",
            auth=("api", "e32fd32058bda5a6f902b35da64c128b-8c8e5529-423025de"),
            data={"from": "Smile_Cook Admin<tonnieblair12@gmail.com>",
                "to": ["kiplimo.antony@students.kyu.ac.ke",],
                "subject": "Yoow",
                "text": "Booyakashaaaaa!"})




class MailgunApi:
    API_URL = "https://api.mailgun.net/v3/{}/messages"
    def __init__(self, domain, api_key):
        self.domain = domain
        self.key = api_key
        self.base_url = self.API_URL.format(self.domain)
    def send_email(self, to, subject, text, html=None):
        if not isinstance(to, (list, tuple)):
            to=[to, ]
        data ={
            "from": "SmileCook<tonnieblair12@gmail.com>",
            "to": to,
            "subject":subject,
            "text": text,
            "html":html
        }
        response = requests.post(url=self.base_url,
                                 auth=('api', self.key),
                                 data=data)
        return response
    
    