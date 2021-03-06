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
    team = data['player']['team']['name']
    code = data['player']['spotcode']

    qr_url = "http://fusiongame.tk/s/%s" % data['player']['touchcode']

    pngpath = "spotter_printer/gen/%s.png" % code
    svgpath = "spotter_printer/gen/%s.svg" % code
    pdfpath = "spotter_printer/gen/%s.pdf" % code



    replacements = {
        '$playername$': data['player']['name'],
        '$code$': data['player']['spotcode'],
        '$touchcode$': data['player']['touchcode'],
        '$team1$' : "%s %s" % (data['teamScores'][0]['name'], data['teamScores'][0]['score']),
        '$team2$' : "%s %s" % (data['teamScores'][1]['name'], data['teamScores'][1]['score']),
        'test.png': '%s.png' % code,
        '$team$': team,
        }

    for i, line in enumerate(data['eventlist']):
        replacements['$eventlist%s$' % i] = line

    for i in range(len(data['eventlist']), 11):
        replacements['$eventlist%s$' % i] = ''

    replacements['$time$'] = datetime.datetime.now().strftime("%H:%M:%S")

    # Read SVG template to memory
    openpath = 'spotter_printer/template_portrait.svg'
    if data['player']['team']['name'].lower() == 'sinised':
        openpath = 'spotter_printer/template_landscape.svg'
    f = codecs.open(openpath, 'rb', encoding='utf8')
    svg = f.read()
    f.close()

    # Replace texts in SVG
    for marker in replacements:
        value = replacements[marker]
        svg = svg.replace(marker, str(value))

    # Replace events data
#    line = 1
#    for row in data['lastevents'].split("\n"):
#        left, action, right = row.split(">")
#        svg = svg.replace("left%d" % line, left)
#        svg = svg.replace("right%d" % line, right)
#        a = """ xlink:href="#blank"
#       id="icon%s"
#""" % (line)
#        b = """ xlink:href="#%s"
#       id="icon%s"
#""" % (action, line)
#        svg = svg.replace(a, b)
#        line += 1
#        if line > 5:
#            break

    # Write modified SVG to a new file
    f = codecs.open(svgpath, 'wb', encoding='utf8')
    f.write(svg)
    f.close()

    # Generate QR code
    subprocess.call('qr "%s" > %s' % (qr_url, pngpath), shell=True)

    # Generate PDF
    subprocess.call('inkscape --without-gui --export-pdf="%s" "%s"' % (pdfpath, svgpath), shell=True)

    return pdfpath
