#!/usr/bin/python3
import sys
import serial
import re

import gevent
import gevent.pywsgi
import gevent.queue

from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport

class SerialHamlib:
    def __init__(self, port: str) -> None:
        self._ser = serial.Serial(port, timeout=0.5)

    def write_cmd(self, cmd) -> None:
       # TODO add error handling an try catch
        self._ser.write(cmd)

    def get_temperature(self) -> int:
        try:
                self._ser.write(b'HRTP;')
                xx = self._ser.read_until(b'\n')
                temp = int(xx[4:-4], base=10)
                self._ser.reset_input_buffer()
                return temp
        except ValueError:
                return -1
        

    def get_voltage(self) -> float:
        self._ser.write(b'HRVT;')
        xx = self._ser.read_until(b'\n')
        volt = float(xx[4:-4])
        self._ser.reset_input_buffer()
        return volt

    def get_band(self) -> int:
        self._ser.write(b'HRBN;')
        xx = self._ser.read_until(b'\n')
        band = int(xx[4:-3], base=10)
        self._ser.reset_input_buffer()
        return band

    def get_atu_status(self) -> int:
        self._ser.write(b'HRAT;')
        xx = self._ser.read_until(b'\n')
        # print((xx))
        atu = int(chr(xx[4]))
        self._ser.reset_input_buffer()
        return atu

    def set_tune_next(self) -> None:
        self._ser.write(b'HRTU1;')

    def set_auto_tx_data(self, enable: int =1) -> None:
        self._ser.write(b'HRRP1;')

    def get_auto_tx_data(self) -> int:
        self._ser.write(b'HRRP;')
        xx = self._ser.read_until(b'\n')
        # print((xx))
        hrrp = int(chr(xx[4]))
        self._ser.reset_input_buffer()
        return hrrp

    def get_tune_next(self) -> int:
        self._ser.write(b'HRTU;')
        xx = self._ser.read_until(b'\n')
        print(xx)
        tune_next = int(xx[4:-3], base=10)
        self._ser.reset_input_buffer()
        return tune_next

    def get_tune_status(self) -> str:
        self._ser.write(b'HRTS;')
        xx = self._ser.read_until(b'\n')
        return xx[5:-3]

    def get_tx_status(self) -> str:
        self._ser.write(b'HRMX;')
        xx = self._ser.read_until(b'\n')
        # print((xx))
        tx = xx.decode()
        self._ser.reset_input_buffer()
        return tx

    def await_tx_data(self) -> str:
        found_hrrp = False
        while (not found_hrrp):
            xx = self._ser.read_until(b'\n')
            print(xx)
            match = re.search("HRMX",str(xx))
            if match:
                found_hrrp = True


def band_tostr(band: int) -> str:
    if band == 0:
            return "6M"
    elif band == 1:
            return "10M"
    elif band == 2:
            return "12M"
    elif band == 3:
            return "15M"
    elif band == 4:
            return "17M"
    elif band == 5:
            return "20M"
    elif band == 6:
            return "30M"
    elif band == 7:
            return "40M"
    elif band == 8:
            return "60M"
    elif band == 9:
            return "80M"
    elif band == 10:
            return "160M"
    else:
            return "unknown"

rpc = JSONRPCProtocol()
hardrock = SerialHamlib('/dev/ttyUSB0')

print("Temp:", hardrock.get_temperature())
print("Volt:", hardrock.get_voltage())
print("Band:", band_tostr(hardrock.get_band()))
print("ATU:", hardrock.get_atu_status())
tx_status = hardrock.get_tx_status()

match = re.search("HRMX P(\d+) A(\d+) S(\d+) T(\d+)",tx_status)

# print("TX:", tx_status)
if match:
    print("Last transmit stats:")
    print("PEP:", match.group(1))
    print("AVG P:", match.group(2))
    print("SWR: 1:", int(match.group(3)) / 10.0)


if (len(sys.argv) > 1):
    if (sys.argv[1] == "tune"):
        print("tune")
        hardrock.set_tune_next()
        print("tune next:",hardrock.get_tune_next())
        hardrock.set_auto_tx_data()
        print("auto tx:",hardrock.get_auto_tx_data())
        hardrock.await_tx_data()
        print("Tune status:", hardrock.get_tune_status())



dispatcher = RPCDispatcher()
transport = WsgiServerTransport(queue_class=gevent.queue.Queue)

# start wsgi server as a background-greenlet
wsgi_server = gevent.pywsgi.WSGIServer(('0.0.0.0', 8066), transport.handle)
gevent.spawn(wsgi_server.serve_forever)

rpc_server = RPCServerGreenlets(
    transport,
    JSONRPCProtocol(),
    dispatcher
)

@dispatcher.public
def getTemperature():
    return hardrock.get_temperature()

@dispatcher.public
def setTune():
        hardrock.set_tune_next()
        return hardrock.get_tune_next()

@dispatcher.public
def getStatus():
        result = {}
        tx_status = hardrock.get_tx_status()
        match = re.search("HRMX P(\d+) A(\d+) S(\d+) T(\d+)",tx_status)

        # print("TX:", tx_status)
        if match:
                result["pep"] = int(match.group(1))
                result["avg"] = int(match.group(2))
                result["swr"] = int(match.group(3)) / 10.0
                result["temp"] = int(match.group(4))
                result["band"] = band_tostr(hardrock.get_band())

                #print("Last transmit stats:")
                # print("PEP:", match.group(1))
                # print("AVG P:", match.group(2))
                # print("SWR: 1:", int(match.group(3)) / 10.0)
        print(result)
        return result

# in the main greenlet, run our rpc_server
rpc_server.serve_forever()


