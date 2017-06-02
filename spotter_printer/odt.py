#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import os.path
import requests
import subprocess
import time

import re, zipfile

template = ""

def modify_odt(inpath, outpath, replacements, pngfile):
    zin = zipfile.ZipFile (inpath, 'r')
    zout = zipfile.ZipFile (outpath, 'w')
    for item in zin.infolist():
        # Mimetype file HAS to be the first in ODF files
        if item.filename == 'mimetype':
            zout.writestr(item, zin.read(item))
    for item in zin.infolist():
        if item.filename == 'content.xml':
            data = zin.read(item)
            # Replace all occurrences of date in <dc:date>
            for search in replacements:
                substitute = replacements[search]
                data = data.replace(str(search).encode('utf8'), str(substitute).encode('utf8'))
            zout.writestr(item, data)
        elif item.filename.endswith('.png'):
            f = open(pngfile, 'rb')
            zout.writestr(item, f.read())
            f.close()
        elif item.filename != 'mimetype':
            zout.writestr(item, zin.read(item))
    zout.close()
    zin.close()


def generate(data):
    team = data['player']['team']['name']
    code = data['player']['spotcode']

    link = "game.pll.ee"
    qr_url = "http://game.pll.ee/s/%s" % data['player']['touchcode']

    if team == 'CT':
        template = 'spotter_printer/template-CT.odt'
    else:
        template = 'spotter_printer/template-TR.odt'
    pngpath = "spotter_printer/gen/%s.png" % code
    odtpath = "spotter_printer/gen/%s.odt" % code
    pdfpath = "spotter_printer/gen/%s.pdf" % code

    replacements = {
        '$t$': team,
        '$playername$': data['player']['name'],
        '$cd$': data['player']['spotcode'],
        '$lcode$': data['player']['touchcode'],
        '$link$': link
        }

    # Generate QR code
    subprocess.call('qr "%s" > %s' % (qr_url, pngpath), shell=True)

    modify_odt(template, odtpath, replacements, pngpath)

    # Generate PDF
    subprocess.call('unoconv -f pdf --export=ExportFormFields=false "%s"' % (odtpath), shell=True)

    return pdfpath
