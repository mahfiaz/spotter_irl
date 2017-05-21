#!/usr/bin/env python3

import codecs
import datetime
from glob import glob
import json
import os
import random
import re
import requests
import shutil
import time

incoming_dir = '/var/spool/sms/incoming/'
incoming_parsed = '/var/spool/sms/processed/'
outgoing_dir = '/var/spool/sms/outgoing/'


def send_sms(phone, text, message_id=None):
    phone = str(phone)
    if not message_id:
        random.seed()
        message_id = random.randint(100000, 999999)

    # Yep, we are from Estonia. Change as needed.
    if not phone.startswith("372"):
        phone = '372%s' % phone

    # Replace common Estonian non-ASCII characters with
    # non-umlauted ones.<
    replace = u'ÕÄÖÜõäöüŠšŽž'
    replacement = u'OAOUoaouSsZz'

    for i, char in enumerate(replace):
        text = text.replace(char, replacement[i])

    # Strip all remaining non-ascii characters, to avoid costly encoding
    text = re.sub(r'[^\x00-\x7F]', '', text)

    # Truncate to 160 characters if longer.
    text = text[0:159]

    message = "To: %s\n\n%s" % (phone, text)

    # By default you don't have the permissions, add the right
    # user to smsd group.
    f = open(os.path.join(outgoing_dir, str(message_id)), 'w')
    f.write(message)
    f.close()


def receive_sms():
    smslist = []
    filelist = glob(os.path.join(incoming_dir, '*'))
    for path in filelist:
        f = codecs.open(path, 'r', encoding='utf8')
        data = f.read()
        f.close()

        folder, filename = os.path.split(path)
        destination = os.path.join(incoming_parsed, filename)
        shutil.move(path, destination)

        split = data.find("\n\n")
        headers = data[:split]
        contents = data[split+2:]

        number = ''
        sent = ''
        received = ''

        for line in headers.split("\n"):
            header, value = line.split(": ")
            if header == "From":
                number = value
                if number.startswith("372"):
                    number = number[3:]
            elif header == "Sent":
                sent = value
            elif header == "Received":
                received = value

        sms = {
            'number': number,
            'contents': contents,
            'sent': sent,
            'received': received
            }
        smslist.append(sms)
    return smslist


def connector():
    print("SMS server started")

    actually_send = True

    while True:
        smslist = receive_sms()
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for sms in smslist:
            print('%s From %s: %s' % (datestr, sms['number'], sms['contents']))
        data = {'incoming': smslist}
        r = requests.get('http://fusiongame.tk/sms?pass=avf2DA3XeJZmqy9KKVjFdGfU',
                         data=json.dumps(data))
        response = json.loads(r.text)
        for message in response['outgoing']:
            number = message['number']
            contents = message['contents']
            if actually_send:
                send_sms(number, contents)
            print('%s   To %s: %s' % (datestr, number, contents))

        time.sleep(0.5)


if __name__ == "__main__":
    connector()

# Testing
#send_sms(512345, u"Rõõmsat päeva, kuidas läheb")
