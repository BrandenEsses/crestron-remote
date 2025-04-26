from flask import Flask, render_template, request, jsonify
import cipclient,time,os
from config import *
from huesdk import Hue
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen

app = Flask(__name__, template_folder='templates')

def hsv_to_rgb(H, S, V):
    C = V * S  # Chroma
    H_prime = H / 60.0
    X = C * (1 - abs(H_prime % 2 - 1))
    m = V - C

    if 0 <= H_prime < 1:
        r1, g1, b1 = C, X, 0
    elif 1 <= H_prime < 2:
        r1, g1, b1 = X, C, 0
    elif 2 <= H_prime < 3:
        r1, g1, b1 = 0, C, X
    elif 3 <= H_prime < 4:
        r1, g1, b1 = 0, X, C
    elif 4 <= H_prime < 5:
        r1, g1, b1 = X, 0, C
    elif 5 <= H_prime < 6:
        r1, g1, b1 = C, 0, X
    else:
        r1, g1, b1 = 0, 0, 0

    # Convert to RGB values between 0 and 255
    R = int(round((r1 + m) * 255))
    G = int(round((g1 + m) * 255))
    B = int(round((b1 + m) * 255))

    return R, G, B
def init_hue_sdk():
    hue = Hue(bridge_ip=HUE_BRIDGE_IP, username=HUE_USERNAME)
    global groups
    groups = hue.get_groups()
def init_crestron_connection():
    global living_room_cip
    living_room_cip = cipclient.CIPSocketClient(CONTROL_PROCESSOR_HOST, LIVING_ROOM_PANEL_IPID)
    living_room_cip.start()
    time.sleep(1.5)

def init_chromecast_adb():
    global device
    if not os.path.isfile(ADB_KEY_PATH):
        keygen(ADB_KEY_PATH)
    time.sleep(1.5)
    with open(ADB_KEY_PATH) as f:
        priv = f.read()
    with open(ADB_KEY_PATH + '.pub') as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)
    device = AdbDeviceTcp(CHROMECAST_IP, CHROMECAST_ADB_PORT, default_transport_timeout_s=9.)
    device.connect(rsa_keys=[signer], auth_timeout_s=0.1)

with app.app_context():
    init_crestron_connection()
    init_hue_sdk()
    init_chromecast_adb()

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
    print(button_data)
    if("adb" in button_data):
        button_code = JOIN_DICT[button_data]
        device.shell('input keyevent "KEYCODE_WAKEUP"')
        device.shell(f'input keyevent "{button_code}"')
        return ("nothing")
    button_join = JOIN_DICT[button_data]
    living_room_cip.pulse(button_join)
    return ("nothing")

@app.route('/hue', methods = ['GET','POST'])
def hue():
    button_data = request.args.get("button")
    for i in range(len(groups)):
        if(groups[i].name == "Living Room"):
            living_room_group = groups[i]
    light = living_room_group.get_lights()[0]
    if(request.method == 'GET'):
        args = list(request.args.keys())
        if("status" in args):
            current_bri = light.__getattribute__("bri")
            current_hue = light.__getattribute__("hue")
            current_sat = light.__getattribute__("sat")
            H = (current_hue / 65535.0) * 360.0
            S = current_sat / 254.0
            V = current_bri / 254.0
            R, G, B = hsv_to_rgb(H, S, V)
            hex_color = '#{0:02X}{1:02X}{2:02X}'.format(R, G, B)
            return jsonify({"brightness": current_bri,"hue":hex_color})

    if(request.args.get("brightness")):
        brightness = int(request.args.get("brightness"))
        living_room_group.set_brightness(brightness)
    if(request.args.get("color")):
        color = request.args.get("color")
        print(color)
        living_room_group.set_color(hexa=color)
    if(button_data=="living_room_off"):
        living_room_group.off()
    if(button_data=="living_room_on"):
            living_room_group.on()
            living_room_group.set_color(hue = 8632)
            living_room_group.set_brightness(254)
            living_room_group.set_saturation(saturation=117)
    if(button_data=="living_room_toggle"):
        current_bri = light.__getattribute__("bri")
        current_hue = light.__getattribute__("hue")
        current_sat = light.__getattribute__("sat")
        print(current_bri, current_hue, current_sat)
        if living_room_group.is_on:
            living_room_group.off()
        else:
            living_room_group.on()
            living_room_group.set_color(hue = 8632)
            living_room_group.set_brightness(254)
            living_room_group.set_saturation(saturation=117)
            
    return ("nothing")

@app.route('/guacamole', methods = ['GET','POST'])
def guacamole():
    return render_template("guacamole.html")
if __name__ == '__main__':
    app.run()
