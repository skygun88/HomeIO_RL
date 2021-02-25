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

    agents = [light1, light2, roller, heater]
    envs = [brightness, temperature, out_temperature, out_brightness]
    all_devices = agents + envs

    for agent in agents:
        agent.random_choice() # Random initilization
    states = list(map(lambda x: x.state(), all_devices))

    while True:
        ''' --- Collect the state --- '''
        states = list(map(lambda x: x.state(), all_devices)) # Doubly call because of bugs
        names = list(map(lambda x: x.name, all_devices))

        state_dict = dict(map(lambda x, y: (x, y), names, states))
        state_dict_json = json.dumps(state_dict)

        print('Current States ---------')
        for key, val in state_dict.items():
            print(f'{key}: {val}')

        client_socket.sendall(state_dict_json.encode())

        ''' --- Receive action data and execute actions --- '''
        data = client_socket.recv(1024)
        if data.decode() == 'quit':
            break
        actions = json.loads(data.decode())
        for agent in agents:
            agent.actuate(actions[agent.name])
        
        ''' --- Collect the next state --- '''
        time.sleep(0.1) # Memory update delay
        next_state = list(map(lambda x: x.state(), all_devices))
        next_state_dict = dict(map(lambda x, y: (x, y), names, next_state))
        next_statee_dict_json = json.dumps(next_state_dict)

        print('Next States ------------')
        for key, val in next_state_dict.items():
            print(f'{key}: {val}')
        print('------------------------\n')

        client_socket.sendall(next_statee_dict_json.encode())
        # time.sleep(0.5)


    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    main()