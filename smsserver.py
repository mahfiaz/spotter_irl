#!/usr/bin/env python3

import codecs
from glob import glob
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
    #print text


def sms_sender(queue):
    while True:
        sms = queue.get()
        if len(sms) == 2:
            phone, text = sms
            send_sms(phone, text)
        else:
            print("SMS_SENDER: not a tuple in sms_out queue: %s" % sms)


def sms_receiver(queue):
    while True:
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

            event = parse_incoming_sms(number, contents, sent, received)
            queue.put(event)


def connector():
    print("SMS server started")
    actually_send = False

    while True:
        r = requests.get('http://fusiongame.tk/sms')
        print(r.text)
        time.sleep(0.2)

if __name__ == "__main__":
    connector()

# Testing
#send_sms(512345, u"Rõõmsat päeva, kuidas läheb")

