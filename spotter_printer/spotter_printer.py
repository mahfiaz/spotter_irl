#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

import json
import codecs
import os.path
import subprocess

def generate(data):
    team = data['team']
    code = data['spotcode']

    qr_url = "http://fusiongame.tk/s/%s" % data['jailcode']

    pngpath = "gen/%s.png" % code
    svgpath = "gen/%s.svg" % code
    pdfpath = "gen/%s.pdf" % code

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
    f = codecs.open('template.svg', 'rb', encoding='utf8')
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
    subprocess.call('lp -d "%s" "%s"' % (printer, pdfpath), shell=True)


testdata = {
    'team': 'blue',
    'printer': 'PDF',
    'spotcode': "56234",
    'touchcode': "56234-432",
    'jailcode': "56234-432-2345",
    'lastevents': u"robin>spotted>Käsnakalle\nEnts>spotted>UXB\nCamperboy2>jailed>Robin\nToNT>touched>Kalle\nRobin>spotted>Ents",
    'score': {
        'blue': 19,
        'red': 23,
        },
    }

pdf = generate(testdata)
# send_printer(pdf, "PDF")
