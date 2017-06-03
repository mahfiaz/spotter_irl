#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import os.path
import requests
import subprocess
import time

from spotter_printer.odt import generate


def send_printer(pdf, printer="PDF"):
    copies = 2
    subprocess.call('lp -d "%s" -n %d "%s"' % (printer, copies, pdf), shell=True)


def connector():
    print("Printing server started")
    actually_print = True
    successful = False

    while True:
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        r = requests.get('http://game.pll.ee/print?pass=htpT2U8UMpApV852DGSncBP7')
        try:
            response = json.loads(r.text)
            if not successful:
                print('Connected')
            successful = True
        except json.decoder.JSONDecodeError:
            if successful:
                print('Disconnected')
            successful = False
            time.sleep(1)
            continue
        for page in response['print']:
            print(datestr, 'Page printed')
            pdf = generate(page)
            print(pdf)
            if actually_print:
                send_printer(pdf, "PDF")
        time.sleep(0.5)


def test():
    testdata = {'player': {
            'name': 'Villu',
            'spotcode': 2374,
            'touchcode': 2440987,
            'team': {
                'name': 'CT',
                'color': '3399FF'}
        },
        'printer': 'PDF',
        'eventlist': [
            '13:35 Villu pages ',
            '13:34 Volloi puutus Villu ',
            '13:33 Villu pages ',
            '13:30 Volloi värvati '],
        'teamScores': [
            {'name': 'CT', 'score': 0},
            {'name': 'TR', 'score': 2}]
        }
    pdf = generate(testdata)
    send_printer(pdf, "PDF")


if __name__ == "__main__":
    #test()
    connector()
