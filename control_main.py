import socket
import json
import sys
import time
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/utils')
import clr
clr.AddReference('EngineIO')

from EngineIO import *
from device.Section_N import *
from device.Outside import *

HOST = ''
PORT = 55665

def main():
    ''' --- Socket setup --- '''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    client_socket, addr = server_socket.accept()
    print('Connected by', addr)

    ''' --- Device object setup --- '''
    light1 = RoomLight1()
    light2 = RoomLight2()
    roller = RoomRoller()
    brightness = RoomBrightness()
    temperature = RoomTemperature()
    heater = RoomHeater()
    out_temperature = OutsideTemperature()
    out_brightness = OutsideBrightness()

    ''' --- State collection --- '''
    agents = [light1, light2, roller, heater]
    envs = [brightness, temperature, out_temperature, out_brightness]
    all_devices = agents + envs

    # while True:
    states = list(map(lambda x: x.state(), all_devices))
    states = list(map(lambda x: x.state(), all_devices)) # Doubly call because of bugs
    names = list(map(lambda x: x.name, all_devices))

    state_dict = dict(map(lambda x, y: (x, y), names, states))
    state_dict_json = json.dumps(state_dict)

    print('--- Current States --- ')
    for key, val in state_dict.items():
        print(f'{key}: {val}')
    print('------------------------')

    client_socket.sendall(state_dict_json.encode())

    data = client_socket.recv(1024)

    data = json.loads(data.decode())

    print('--- Selected actions --- ')
    for key, val in data.items():
        print(f'{key}: {val}')
    print('------------------------')

    if data[names[0]] == 1:
        light1.on()
        light2.on()

    else:
        light1.off()
        light2.off()


    # client_socket.sendall(data)
    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    main()