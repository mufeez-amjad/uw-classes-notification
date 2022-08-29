import time
from twilio.rest import Client
import ssl
import urllib.request
import re

ssl._create_default_https_context = ssl._create_unverified_context

# Replace this with the term number you find on https://classes.uwaterloo.ca/under.html
term = '1229'

courses = {
    'CS': ['454']
}

# if you want to constrain your search to be for an online section, same format as `courses`
online = {}

# Create a free Twilio account and paste credentials here.
account_sid = ''
auth_token = ''

my_phone_number = '+1234567890'

MAX_CALLS = 5
MAX_RING_PINGS = 10

class TwilioClient:
    def __init__(self):
        self.client = Client(account_sid, auth_token)
        # Taken from your Twilio account
        self.from_num = '+1234567890'

    def get_call_log(self, call_sid: str):
        c = self.client.calls(call_sid).fetch()
        return {'sid': c.sid, 'status': c.status, 'from': c.from_, 'to': c.to}

    def message(self, message: str) -> None:
        if message:
            self.client.messages.create(
                body=message,
                from_=self.from_num,
                to=my_phone_number
            )

    def call(self) -> None:
        call_count = 0
        while True:
            call = self.client.calls.create(
                url='http://demo.twilio.com/docs/voice.xml',
                to=my_phone_number,
                from_=self.from_num
            )
            call_count += 1

            ring_count = 0
            while True:
                log = self.get_call_log(call.sid)

                if log['status'] == 'ringing':
                    ring_count += 1

                if log['status'] not in ['ringing', 'queued', 'in-progress']:
                    break
                else:
                    if ring_count > MAX_RING_PINGS:
                        break
                    time.sleep(1)

            if call_count > MAX_CALLS or ring_count < MAX_RING_PINGS:
                break

tw = TwilioClient()

base_url = 'https://info.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?sess='
message = ''
call_me = False
for faculty in courses:
    for course in courses[faculty]:
        url = base_url + term + '&level=under&subject=' + faculty + '&cournum=' + course
        webpage = urllib.request.urlopen(url)
        for i in webpage.readlines():
            if '<TD>' in str(i) and 'LEC' in str(i):
                if faculty in online and course in online[faculty] and 'ONLINE' not in str(i):
                    pass # only look for online offering of course
                else:
                    x = str(i).split('<TD ALIGN="center">')
                    section = re.sub('<[^<]+?>', '', x[2]).strip()
                    enrolled = re.sub('<[^<]+?>', '', x[6]).strip()
                    total_spots = re.sub('<[^<]+?>', '', x[5]).strip()
                    print(f'{enrolled}/{total_spots}')
                    spots_left = int(total_spots) - int(enrolled)
                    if spots_left > 0:
                        call_me = True
                        message += f'{spots_left} spots open in {faculty}{course} {section}!\n'

if message:
    tw.message(message)
if call_me:
    tw.call()
