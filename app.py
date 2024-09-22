from flask import Flask, render_template, request
import cipclient,time,os
from config import *
from huesdk import Hue
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen
from samsungtvws import SamsungTVWS

app = Flask(__name__, template_folder='templates')

def init_hue_sdk():
    hue = Hue(bridge_ip=HUE_BRIDGE_IP, username=HUE_USERNAME)
    global groups
    groups = hue.get_groups()
def init_crestron_connection():
    global living_room_cip
    living_room_cip = cipclient.CIPSocketClient(CONTROL_PROCESSOR_HOST, LIVING_ROOM_PANEL_IPID)
    living_room_cip.start()
    time.sleep(1.5)

with app.app_context():
    init_crestron_connection()
    init_hue_sdk()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/living_room')
def living_room():
    return render_template('rooms/living_room.html')

@app.route('/bedroom')
def bedroom():
    return render_template('rooms/bedroom.html')

@app.route('/living_room_join_handler', methods = ['POST'])
def living_room_join_handler():
    button_data = request.args.get("button")
    button_join = JOIN_DICT[button_data]
    living_room_cip.pulse(button_join)
    return ("nothing")

@app.route('/hue', methods = ['POST'])
def hue():
    button_data = request.args.get("button")
    for i in range(len(groups)):
        if(groups[i].name == "Living Room"):
            living_room_group = groups[i]
    if(request.args.get("brightness")):
        brightness = int(request.args.get("brightness"))
        living_room_group.set_brightness(brightness)
    if(button_data=="living_room_off"):
        living_room_group.off()
    if(button_data=="living_room_on"):
        living_room_group.on()
        living_room_group.set_color(hexa="#f5d269")
        living_room_group.set_brightness(254)
    return ("nothing")

if __name__ == '__main__':
    app.run()
