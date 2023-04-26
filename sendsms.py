import requests

class Fast2SMS:

    def __init__(self, api_key):
        self.api_key = api_key

    def send_sms(self, to_number, message):
        url = 'https://www.fast2sms.com/dev/bulkV2'
        payload = {
            'sender_id': 'FSTSMS',
            'message': message,
            'language': 'english',
            'route': 'p',
            'numbers': to_number
        }
        headers = {
            'authorization': self.api_key,
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        return response.text
