import socket
import json
import sys
import time
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/utils')
import clr
clr.AddReference('EngineIO')

from datetime import datetime
from EngineIO import *
from device.Section_N import *
from device.Outside import *
from user_main import working_feedback

HOST = ''
PORT = 55665

def main(sl_flag=False):
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

    current_time = str(datetime.now()).replace(':', '_').split('.')[0]
    f = open('user_log_'+current_time+'.csv', 'w')
    if sl_flag:
        sf = open('state_log_'+current_time+'.txt', 'w')

    for agent in agents:
            agent.random_choice() # Random initilization
    time.sleep(0.1)
    states = list(map(lambda x: x.state(), all_devices))
    time.sleep(1)
    states = list(map(lambda x: x.state(), all_devices))
    print(f'initial state: {states}')
    if sl_flag:
        sf.write(f'initial state: {states}\n')

    while True:
        ''' --- Collect the state --- '''
        states = list(map(lambda x: x.state(), all_devices)) # Doubly call because of bugs
        names = list(map(lambda x: x.name, all_devices))

        state_dict = dict(map(lambda x, y: (x, y), names, states))
        state_dict_json = json.dumps(state_dict)

        client_socket.sendall(state_dict_json.encode())

        ''' --- Receive action data and execute actions --- '''
        data = client_socket.recv(1024)
        if data.decode() == 'quit':
            break
        if data.decode() == 'train':
            states = list(map(lambda x: x.state(), all_devices))
            action_cnt, final_state = working_feedback(states, all_devices)
            time.sleep(0.1)
            final_state_dict = dict(map(lambda x, y: (x, y), names, final_state))
            final_state_dict_json = json.dumps(final_state_dict)

            print(f'agents\' final state: {states}')
            print(f'User\'s action: {action_cnt}')
            print(f'users\' final state: {final_state}')
            print('------------------------')

            if sl_flag:
                sf.write(f'agents\' final state: {states}\n')
                sf.write(f'User\'s action: {action_cnt}\n')
                sf.write(f'users\' final state: {final_state}\n')
                sf.write('------------------------\n')            
            
            client_socket.sendall(final_state_dict_json.encode())
            client_socket.sendall(json.dumps({'user_cnt': action_cnt}).encode())
            f.write(','.join(list(map(lambda x: str(x), action_cnt))))
            f.write('\n')

            for agent in agents:
                agent.random_choice() # Random initilization
            
            time.sleep(0.1)
            #time.sleep(30)
            states = list(map(lambda x: x.state(), all_devices))
            print(f'initial state: {states}')
            if sl_flag:
                sf.write(f'initial state: {states}\n')
            continue

        actions = json.loads(data.decode())
        for agent in agents:
            agent.actuate(actions[agent.name])
        
        ''' --- Collect the next state --- '''
        time.sleep(0.1) # Memory update delay
        next_state = list(map(lambda x: x.state(), all_devices))
        next_state_dict = dict(map(lambda x, y: (x, y), names, next_state))
        next_state_dict_json = json.dumps(next_state_dict)

        client_socket.sendall(next_state_dict_json.encode())
        # time.sleep(0.5)
    
    
    f.close()
    if sl_flag:
        sf.close()
    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    for _ in range(3):
        main(sl_flag=False)