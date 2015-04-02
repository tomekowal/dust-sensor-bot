import logging
import serial

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
import socket
import time

CARBON_SERVER = '31.172.186.54'
CARBON_PORT = 2003

class DustSensorBot(ClientXMPP):
    def __init__(self, jid, password, room, nick):
        ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.nick = nick
        self.add_event_handler("session_start", self.session_start)

    def session_start(self, event):
        retval = self.get_roster()
        retval = self.send_presence()
        retval = self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)
        print retval

def send_msg(message):
    print 'sending message to graphite:\n%s' % message
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    sock.close()

if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    room = 'malopolska@muc.localhost'
    xmpp = DustSensorBot('dust_sensor@localhost', 'dust_sensor', room, 'dust_sensor')
    xmpp.register_plugin('xep_0045')
    xmpp.connect((CARBON_SERVER, 5222))
    xmpp.process(block=False)
    ser = serial.Serial('/dev/ttyACM0', 9600) # Establish the connection on a specific port

    while True:
        dust_concentration = ser.readline().strip() # Read the newest output from the Arduino
        print dust_concentration, " particles per cubic feet"
        retval = xmpp.send_message(mto=room, mbody=str(dust_concentration), mtype="groupchat")
        timestamp = int(time.time())
        message = 'dust_sensor.concentration %s %d\n' % (dust_concentration, timestamp)
        send_msg(message)
