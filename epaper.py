#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import configparser
import fasteners
import traceback

from rpi_epd2in7.epd2in7 import EPD
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

config = configparser.ConfigParser()
config.read('/home/pi/Prog/bin/rpi_config.ini')

PROGDIR = config.get('PATH', 'PROGDIR')
EPAPERDIR = config.get('PATH', 'EPAPERDIR')
LOCKFILE = PROGDIR + '/lockepaper'
NOEPAPER = config.get('DISP', 'NOEPAPER')
MAINNET = config.get('PATH', 'MAINNET')

# 176x264
FONT_FILE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TITLE_Y = 0
TITLE_SZ = 18

# date
DATE_SZ = 14
DATE_POS = (0, 250)

# logo
PTARM_FILE = EPAPERDIR + '/ptarm176x264.png'
PTARM_POS = (0, 0)
LOGO_FILE = EPAPERDIR + '/logo.png'
LOGOT_FILE = EPAPERDIR + '/logo_testnet.png'
LOGO_POS = (2, 215)

# ipaddr
IP_FILE = PROGDIR + '/ipaddr.txt'
IP_SZ = 14
IP_POS = (50, 230)


def disp_qrcode(png_file, title_str, clear_frame):
    if os.path.isfile(NOEPAPER):
        print('no epaper mode')
        return
    lock = fasteners.InterProcessLock(LOCKFILE)
    if not lock.acquire():
        print('now using')
        return

    try:
        print('init')
        epd = EPD()
        epd.init()

        if clear_frame:
            print('clear')
            epd.Clear(0xFF)

        elif (len(png_file) == 0) and (len(title_str) == 1) and (len(title_str[0]) == 0):
            print('splash')
            image = Image.open(PTARM_FILE);
            epd.display(epd.getbuffer(image))

        else:
            image = Image.new('1', (epd.width, epd.height), 255)
            image = _disp_image(epd, image, png_file)
            image = _disp_title(epd, image, title_str)
            image = _disp_datetime(epd, image)
            image = _disp_logo(epd, image)
            image = _disp_ipaddr(epd, image)
            print('display')
            epd.display(epd.getbuffer(image))

        epd.sleep()
    except:
        print('exception')
        print('traceback.format_exc():\n%s' % traceback.format_exc())

    lock.release()


def _disp_image(epd, image, png_file):
    if os.path.isfile(png_file):
        print('PNG file' + png_file)
        img = Image.open(png_file);
        px = int((epd.width - img.size[0]) / 2)
        py = int((epd.height - img.size[1]) / 2)
        image.paste(img, (px, py))
    return image


def _disp_title(epd, image, title_str):
    if len(title_str) > 0:
        print('title')
        print(title_str)
        draw = ImageDraw.Draw(image)
        imgfont = ImageFont.truetype(FONT_FILE, TITLE_SZ)
        height = TITLE_Y
        for title in title_str:
            if title.isdecimal():
                title = '{:,}'.format(int(title))
            draw_sz = draw.textsize(title, font = imgfont)
            draw_pos = ((epd.width - draw_sz[0]) / 2, height)
            draw.text(draw_pos, title, font = imgfont, fill = 0)
            height += TITLE_SZ
    return image


def _disp_datetime(epd, image):
    now = datetime.now()
    draw = ImageDraw.Draw(image)
    imgfont = ImageFont.truetype(FONT_FILE, DATE_SZ)
    date_str = now.strftime('%Y/%m/%d') + '  ' + now.strftime('%H:%M:%S')
    draw.text(DATE_POS, date_str, font = imgfont, fill = 0)
    return image


def _disp_logo(epd, image):
    if os.path.isfile(MAINNET):
        ptarm = Image.open(LOGO_FILE);
    else:
        ptarm = Image.open(LOGOT_FILE);
    image.paste(ptarm, LOGO_POS)
    return image


def _disp_ipaddr(epd, image):
    try:
        ipaddr = ''
        with open(IP_FILE) as f:
            ipaddr = f.read()
        print('ipaddr=' + ipaddr)
        imgfont = ImageFont.truetype(FONT_FILE, IP_SZ)
        draw = ImageDraw.Draw(image)
        draw.text(IP_POS, ipaddr, font = imgfont, fill = 0)
    except:
        pass
    return image


# arg none: clear
# arg[1]: PNG filename
# arg[2]: title(default 'invoice')
def main():
    print('start')
    clear_frame = False
    png_file = ''
    title_str = ['invoice']
    if len(sys.argv) == 1:
        clear_frame = True
    else:
        png_file = sys.argv[1]
    if len(sys.argv) >= 3:
        title_str = sys.argv[2:]

    disp_qrcode(png_file, title_str, clear_frame)


if __name__ == '__main__':
    main()
