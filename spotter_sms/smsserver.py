#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

import random
import re

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
    f = open('/var/spool/sms/outgoing/%s' % str(message_id), 'w')
    f.write(message)
    f.close()
    #print text



# Testing
#send_sms(512345, u"Rõõmsat päeva, kuidas läheb")
