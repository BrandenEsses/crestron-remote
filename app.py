from flask import Flask, render_template, request
import cipclient,time,os
from config import *
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen
from samsungtvws import SamsungTVWS

app = Flask(__name__, template_folder='templates')

def init_crestron_connection():
    global living_room_cip
    living_room_cip = cipclient.CIPSocketClient(CONTROL_PROCESSOR_HOST, LIVING_ROOM_PANEL_IPID)
    living_room_cip.start()
    time.sleep(1.5)

with app.app_context():
    init_crestron_connection()

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

if __name__ == '__main__':
    app.run()
