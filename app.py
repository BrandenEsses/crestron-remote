from flask import Flask, render_template, request
import cipclient,time
from config import CONTROL_PROCESSOR_HOST, LIVING_ROOM_PANEL_IPID, BEDROOM_PANEL_IPID, JOIN_DICT

app = Flask(__name__, template_folder='templates')

with app.app_context():
    global living_room_cip
    living_room_cip = cipclient.CIPSocketClient(CONTROL_PROCESSOR_HOST, LIVING_ROOM_PANEL_IPID)
    living_room_cip.start()
    time.sleep(1.5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/living_room')
def living_room():
    return render_template('rooms/living_room.html')

@app.route('/bedroom')
def bedroom():
    return render_template('rooms/bedroom.html')

@app.route('/join_handler', methods = ['POST'])
def join_handler():
    button_data = request.args.get("button")
    button_join = JOIN_DICT[button_data]
    living_room_cip.pulse(button_join)
    return ("nothing")

if __name__ == '__main__':
    app.run()
