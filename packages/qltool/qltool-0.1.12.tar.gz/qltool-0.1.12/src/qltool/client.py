#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from qltool.main import cli
#from qltool.main import is_user_in_lp_group
#is_user_in_lp_group()


from click.testing import CliRunner
import inspect
from qltool.main import cli  # your click Command object

from console import fg, bg
import shlex

broker = "127.0.0.1"
topic = "qltool/print"

# ======================================================================
#
# ----------------------------------------------------------------------
def call_with_runner(args):
    """
    args: list of command-line tokens, e.g. ['line1','line2','--qr-create']
    """
    runner = CliRunner()
    result = runner.invoke(cli, args)
    return result.exit_code, result.output, result.exception



# ======================================================================
#
# ----------------------------------------------------------------------
def on_message(client, userdata, msg):

    data = msg.payload
    #data_block = decode_payload(data)
    #image = data_block['image']

    text = data.decode("utf8")

    blocks = shlex.split(text)
    print(blocks)

    FS = None
    Q = False
    P = False
    lines = []
    for i, obj in enumerate(blocks):

        print(f"#{i}# {obj}")

        if obj.find("-") < 0:
            lines.append(obj)
        elif obj == "-q":
            print("create qr")
            Q = True
            lines.append("-q")
        elif obj == "-p":
            print("print")
            lines.append("-p")
            P = True
        elif obj == "--font-size":
            FS = obj[i + 1]

    if FS is None:
        FS = 72

    print( f" {lines}, {FS}, create qr ={Q}, print {P}")
    #cli( lines, font_size=FS, qr_create=Q, do_print=P)
    #cli( lines,  qr_create=Q, do_print=P)
    res = call_with_runner( lines  )
    for i in res:
        print(i)
    print("")
    print(fg.orange, "WAITING ON COMMANDS VIA MQTT...... ", fg.default)

    #print( flush=True)
    #cv2.imshow("Received Image", image)
    #cv2.waitKey(10)  # Needed to refresh window


def main():
    print(fg.orange, "WAITING ON COMMANDS VIA MQTT...... ", fg.default)
    print(f"  topic:  {topic}")
    print(f"  broker:  {broker}")

    print("""   ### examples:
    export D=`date +"%H:%M:%S"`; mosquitto_pub -t qltool/print -m "hoho $D -q -p"

    # blocking...
    mosquitto_pub -t qltool/print -m "hoho secondline thirdline  -q "
    #  NEVER USE THIS:
    # watch -n 10 'export D=`date +"%H:%M:%S"`; mosquitto_pub -t qltool/print -m "\"hoho asdas\" \"jeli $D\"  -q "'
    """)
    print(fg.orange, "WAITING ON COMMANDS VIA MQTT...... ", fg.default)
    client = mqtt.Client()
    client.on_message = on_message

    client.connect(broker, 1883, 60)
    client.subscribe(topic)
    client.loop_forever()

if __name__ == "__main__":
    main()
