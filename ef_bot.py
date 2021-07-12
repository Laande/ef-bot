#####

# Commands :

CMD_SET = "/ef set"
CMD_SIDE = "/ef side"
CMD_ON = "/ef on"
CMD_RESET = "/ef reset"

####

import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction
from g_python.hparsers import HFloorItem

extension_info = {
    "title": "EF Bot",
    "description": "idk",
    "version": "2.0",
    "author": "Lande"
}

ext = Extension(extension_info, sys.argv)
ext.start()


on, wait, side = False, False, False
x_list, y_list = [], []
count = 0


def talk(msg):
    ext.send_to_client('{in:Whisper}{i:9999999}{s:"@red@'+msg+'"}{i:0}{i:30}{i:0}{i:0}')


def speech(p):
    global wait, side, on, count

    msg, _, _ = p.packet.read('sii')

    if msg.startswith(CMD_SET):
        block(p)
        wait = True
        talk("Click on the 4 rollers")

    if msg.startswith(CMD_SIDE):
        block(p)
        if side:
            side = False
            talk("Set to right")
        else:
            side = True
            talk("Set to left")

    if msg.startswith(CMD_ON):
        block(p)
        if on:
            on = False
        else:
            on = True
        talk(f"{on=}")

    if msg.startswith(CMD_RESET):
        block(p)
        reset()
        talk("Reset.")


def walk(p):
    global wait, count

    if wait:
        block(p)
        x, y = p.packet.read('ii')
        talk(f"{count+1}. {x=} {y=}")
        x_list.append(x)
        y_list.append(y)
        count += 1
        if count == 4:
            talk("Done.")
            wait = False
            count = 0


def update(p):
    if on:
        furni = HFloorItem(p.packet)
        x_furni, y_furni = furni.tile.x, furni.tile.y
        for i, k in zip(x_list, y_list):
            if side:
                if x_furni == i and y_furni == k:
                    ext.send_to_server('{out:MoveAvatar}{i:'+str(i)+'}{i:'+str(k-1)+'}')
            else:
                if x_furni == i and y_furni == k:
                    ext.send_to_server('{out:MoveAvatar}{i:'+str(i)+'}{i:'+str(k+1)+'}')


def reset():
    global on, wait, side, x_list, y_list, count

    on, wait, side = False, False, False
    x_list, y_list = [], []
    count = 0


def r(p):
    reset()


def block(p):
    p.is_blocked = True


ext.intercept(Direction.TO_SERVER, walk, 'MoveAvatar')
ext.intercept(Direction.TO_SERVER, speech, 'Chat')
ext.intercept(Direction.TO_CLIENT, update, 'ObjectUpdate')
ext.intercept(Direction.TO_SERVER, r, 'GetHeightMap')
