import zmq
import time

from datetime import datetime

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

var1 = 0.0
var2 = 0.0

while True:
    var1 = var1 + 0.22
    var2 = var2 + 0.221
    msg = str(datetime.now().timestamp()) + "|" + str(var1) + "|" + str(var2)
    socket.send_string(msg)
    print(f"Sent: {msg}")
    time.sleep(0.005)
