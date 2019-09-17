from __future__ import print_function
from rpi_epd2in7_partial.epd import EPD
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
import configparser
import fasteners


config = configparser.ConfigParser()
config.read('/home/pi/Prog/bin/rpi_config.ini')
PROGDIR = config.get('PATH', 'PROGDIR')
LOCKFILE = PROGDIR + '/lockepaper'
NODEDIR = config.get('PATH', 'NODEDIR')
LOGFILE = NODEDIR + '/logs/bitcoinj_startup.log'

PROGVER = config.get('PATH', 'PROGVER')
PTARMVER = config.get('PATH', 'PTARMVER')
BINVER = config.get('PATH', 'BINVER')
EPAPERVER = config.get('PATH', 'EPAPERVER')
UARTVER = config.get('PATH', 'UARTVER')
WEBVER = config.get('PATH', 'WEBVER')

DISP_Y = 40
FONT_HEIGHT = 16

UPDATE_NONE = 0
UPDATE_STOP = 1
UPDATE_CONT = 2


def main():
    lock = fasteners.InterProcessLock(LOCKFILE)
    if not lock.acquire():
        print('now using')
        return

    print("initializing", end="")
    sys.stdout.flush()
    epd = EPD()
    epd.init()
    print(".", end="")
    sys.stdout.flush()

    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    title(epd, image, draw)
    epd.display_frame(image)
    print(".")

    font = ImageFont.truetype('/usr/share/fonts/truetype/DejaVuSans-Bold.ttf', 13)
    prev_info = ''
    info = ''
    loc_y = DISP_Y
    loc_x = 0

    ver = ''
    draw.text((loc_x, loc_y), 'Version:', font=font, fill=0)
    loc_y += FONT_HEIGHT
    with open(PROGVER) as f:
        ver = f.read()
        draw.text((loc_x, loc_y), '  ' + ver, font=font, fill=0)
        loc_y += FONT_HEIGHT

    draw.text((loc_x, loc_y), 'ptarmigan:', font=font, fill=0)
    loc_y += FONT_HEIGHT
    with open(PTARMVER) as f:
        ver = f.read()
        draw.text((loc_x, loc_y), '  ' + ver, font=font, fill=0)
        loc_y += FONT_HEIGHT

    draw.text((loc_x, loc_y), 'bin:', font=font, fill=0)
    loc_y += FONT_HEIGHT
    with open(BINVER) as f:
        ver = f.read()
        draw.text((loc_x, loc_y), '  ' + ver, font=font, fill=0)
        loc_y += FONT_HEIGHT

    draw.text((loc_x, loc_y), 'epaper:', font=font, fill=0)
    loc_y += FONT_HEIGHT
    with open(EPAPERVER) as f:
        ver = f.read()
        draw.text((loc_x, loc_y), '  ' + ver, font=font, fill=0)
        loc_y += FONT_HEIGHT

    draw.text((loc_x, loc_y), 'uart:', font=font, fill=0)
    loc_y += FONT_HEIGHT
    with open(UARTVER) as f:
        ver = f.read()
        draw.text((loc_x, loc_y), '  ' + ver, font=font, fill=0)
        loc_y += FONT_HEIGHT

    draw.text((loc_x, loc_y), 'web:', font=font, fill=0)
    loc_y += FONT_HEIGHT
    with open(WEBVER) as f:
        ver = f.read()
        draw.text((loc_x, loc_y), '  ' + ver, font=font, fill=0)
        loc_y += FONT_HEIGHT * 2

    while True:
        prev_info = info
        info = ''
        update = UPDATE_NONE
        try:
            with open(LOGFILE) as f:
                info = f.read()
            info = info.rstrip('\n')
            print('info="' + info + '"')
        except:
            pass
        if info[:5] == 'STOP=':
            info = info[5:]
            update = UPDATE_STOP
        elif info[:5] == 'CONT=':
            info = info[5:]
            update = UPDATE_CONT
        elif info[:6] == 'BLOCK=':
            info = info[6:]
            update = UPDATE_CONT

        if (update != UPDATE_NONE) and (prev_info != info):
            disp = 0
            if loc_y > epd.height - 30:
                # 次列 or frame更新
                loc_y = DISP_Y
                if loc_x == 0:
                    # 次列
                    loc_x = epd.width / 2
                else:
                    # frame更新
                    loc_x = 0
                    image = Image.new('1', (epd.width, epd.height), 255)
                    draw = ImageDraw.Draw(image)
                    title(epd, image, draw)
                    disp = 1

            draw.text((loc_x, loc_y), info.ljust(12), font=font, fill=0)
            if disp == 0:
                epd.smart_update(image)
            elif disp == 1:
                epd.display_frame(image)
            loc_y += FONT_HEIGHT

            print(".", end="")
            sys.stdout.flush()
        if update == UPDATE_STOP:
            break
        epd.delay_ms(1000)

    epd.sleep()
    print("!")

    lock.release()


def title(epd, image, draw):
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    draw.text((0, 5), 'Syncing...', font=font, fill=0)
    draw.line([0, 28, epd.width, 28], fill=0, width=3)


if __name__ == '__main__':
    main()
