#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import os.path
import requests
import subprocess
import time

def generate(data):
    team = data['team']
    code = data['spotcode']

    qr_url = "http://fusiongame.tk/s/%s" % data['jailcode']

    pngpath = "spotter_printer/gen/%s.png" % code
    svgpath = "spotter_printer/gen/%s.svg" % code
    pdfpath = "spotter_printer/gen/%s.pdf" % code

    replacements = {
        '$code$': data['spotcode'],
        '$touchcode$': data['touchcode'],
        '$bs$': data['score']['blue'],
        '$rs$': data['score']['red'],
        'test.png': '%s.png' % code,
        }

    if team == 'blue':
        replacements['$team$'] = 'siniste'
    else:
        replacements['$team$'] = 'punaste'


    # Read SVG template to memory
    f = codecs.open('spotter_printer/template.svg', 'rb', encoding='utf8')
    svg = f.read()
    f.close()

    # Replace texts in SVG
    for marker in replacements:
        value = replacements[marker]
        svg = svg.replace(marker, str(value))

    # Replace events data
    line = 1
    for row in data['lastevents'].split("\n"):
        left, action, right = row.split(">")
        svg = svg.replace("left%d" % line, left)
        svg = svg.replace("right%d" % line, right)
        a = """ xlink:href="#blank"
       id="icon%s"
""" % (line)
        b = """ xlink:href="#%s"
       id="icon%s"
""" % (action, line)
        svg = svg.replace(a, b)
        line += 1
        if line > 5:
            break

    # Write modified SVG to a new file
    f = codecs.open(svgpath, 'wb', encoding='utf8')
    f.write(svg)
    f.close()

    # Generate QR code
    subprocess.call('qr "%s" > %s' % (qr_url, pngpath), shell=True)

    # Generate PDF
    subprocess.call('inkscape --without-gui --export-pdf="%s" "%s"' % (pdfpath, svgpath), shell=True)

    return pdfpath


def send_printer(pdf, printer="PDF"):
    subprocess.call('lp -d "%s" "%s"' % (printer, pdf), shell=True)


def connector():
    print("Printing server started")
    actually_print = True

    while True:
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        r = requests.get('http://localhost:5000/print?pass=htpT2U8UMpApV852DGSncBP7')
        response = json.loads(r.text)
        for page in response['print']:
            print(datestr, 'Page printed')
            pdf = generate(page)
            print(pdf)
            if actually_print:
                send_printer(pdf, "PDF")

        time.sleep(0.5)


if __name__ == "__main__":
    connector()

test = """
{'player': {
    'name': 'Villu', 
    'spotcode': 2374, 
    'touchcode': 2440987, 
    'team': {
        'name': 'Sinised', 
        'color': '3399FF'}}, 
    'printer': 'PDF', 
    'eventlist': [
        '13:35 Villu pages ', 
        '13:34 Volloi puutus Villu ', 
        '13:33 Villu pages ', 
        '13:30 Volloi värvati '], 
    'teamScores': [
        {'name': 'Sinised', 'score': 0}, 
        {'name': 'Punased', 'score': 2}]
    }
"""


#pdf = generate(testdata)
# send_printer(pdf, "PDF")
