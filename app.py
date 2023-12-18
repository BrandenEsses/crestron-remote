from flask import Flask, render_template, request
import cipclient,time,os
from config import *
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen
from samsungtvws import SamsungTVWS

app = Flask(__name__, template_folder='templates')

with app.app_context():
    global living_room_cip, device, tv
    if not os.path.isfile(ADB_KEY_PATH):
        keygen(ADB_KEY_PATH)
    living_room_cip = cipclient.CIPSocketClient(CONTROL_PROCESSOR_HOST, LIVING_ROOM_PANEL_IPID)
    living_room_cip.start()
    time.sleep(1.5)
    with open(ADB_KEY_PATH) as f:
        priv = f.read()
    with open(ADB_KEY_PATH + '.pub') as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)
    device = AdbDeviceTcp(CHROMECAST_IP, CHROMECAST_ADB_PORT, default_transport_timeout_s=9.)
    device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
    # tv = SamsungTVWS(BEDROOM_TV_IP)
    if not os.path.isfile(BEDROOM_TV_TOKEN_FILE_PATH):
        with open(BEDROOM_TV_TOKEN_FILE_PATH, 'w') as fp:
            pass
    tv = SamsungTVWS(host=BEDROOM_TV_IP, port=BEDROOM_TV_PORT, token_file=BEDROOM_TV_TOKEN_FILE_PATH)
    tv.shortcuts().volume_down()

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
    if "adb" in button_data:
        if "vol_up" in button_data:
            response = device.shell('input keyevent "KEYCODE_VOLUME_UP"')
        if "vol_down" in button_data:
            response = device.shell('input keyevent "KEYCODE_VOLUME_DOWN"')
        if "vol_mute" in button_data:
            response = device.shell('input keyevent "KEYCODE_VOLUME_MUTE"')
        return ("nothing")
    if 'source_select' in button_data and not living_room_cip.get("d",59):
        response = device.shell('input keyevent "KEYCODE_POWER"')
        time.sleep(0.25)
    button_join = JOIN_DICT[button_data]
    living_room_cip.pulse(button_join)
    return ("nothing")

@app.route('/bedroom_join_handler', methods = ['POST'])
def bedroom_join_handler():
    button_data = request.args.get("button")
    if 'bedroom_tv' in button_data:
        if 'vol_up' in button_data:
            tv.shortcuts().volume_up()
        if 'vol_down' in button_data:
            tv.shortcuts().volume_down()
        if 'vol_mute' in button_data:
            tv.shortcuts().mute()
        if 'up' in button_data:
            tv.shortcuts().up()
        if 'down' in button_data:
            tv.shortcuts().down()
        if 'left' in button_data:
            tv.shortcuts().left()
        if 'right' in button_data:
            tv.shortcuts().right()
        if 'select' in button_data:
            tv.shortcuts().enter()
    button_join = JOIN_DICT[button_data]
    living_room_cip.pulse(button_join)
    return ("nothing")

if __name__ == '__main__':
    app.run()
