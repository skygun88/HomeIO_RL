import socket
import json
from RL.table_agent import *
import os
from datetime import datetime
import time

HOST = '127.0.0.1'
PORT = 55665

BRIGHTNESS_N_STATE = 5
TEMPERATURE_N_STATE = 3
N_ACTION = 3
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
WEIGHT_PATH = CURRENT_PATH+'/weight/'
N_LEVEL = 10


def state_preprocessing(states, n_level):
    brightness_env = list(filter(lambda x: 'Brightness' in x[0], states.items()))
    temperature_env = list(filter(lambda x: 'Temperature' in x[0], states.items()))
    brightness_env_state = list(map(lambda x: min(int(min(max(x[1], 0), 10)/(10/n_level)), n_level-1), brightness_env)) # clip (0 ~ 10)/10
    temperature_env_state = list(map(lambda x: min(int((min(max(x[1], -10), 30)+10)/(40/n_level)), n_level-1), temperature_env)) # (clip (-10, 30)+10)/40

    light_agent_state = list(map(lambda x: min(int(x[1]/(10/n_level)), n_level-1), states.items()))[:2]
    roller_agent_state = [min(int(states['RoomRoller']/(10/2)), 1)]
    temperature_agent_state = [min(int(states['RoomHeater']/(10/n_level)), n_level-1)]

    brigthness_state = light_agent_state + roller_agent_state + brightness_env_state
    temperature_state = temperature_agent_state + temperature_env_state
    return brigthness_state, temperature_state



def main(load_flag=False, save_flag=True, maximum_episode=100):
    ''' --- Socket setup --- '''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    ''' --- Agent setup --- '''
    light1 = TabulatedIotAgent(BRIGHTNESS_N_STATE, N_ACTION, 'RoomLight1')
    light2 = TabulatedIotAgent(BRIGHTNESS_N_STATE, N_ACTION, 'RoomLight2')
    roller = TabulatedIotAgent(BRIGHTNESS_N_STATE, N_ACTION, 'RoomRoller')
    heater = TabulatedIotAgent(TEMPERATURE_N_STATE, N_ACTION, 'RoomHeater')

    agents = [light1, light2, roller, heater]

    ''' load or pretrain the model'''
    if load_flag == True:
        light1.load_model(WEIGHT_PATH)
        light2.load_model(WEIGHT_PATH)
        roller.load_model(WEIGHT_PATH)
        heater.load_model(WEIGHT_PATH)


    current_time = str(datetime.now()).replace(':', '_').split('.')[0]
    f = open('agent_log_'+current_time+'.csv', 'w')

    for i in range(maximum_episode):
        print(f'[{i+1}] Episode start')
        light1.memory = []
        light2.memory = []
        roller.memory = []
        heater.memory = []
        actions = [-1]*4
        actions_cnt = [0]*4
        while True:
            ''' --- State data received --- '''
            data = client_socket.recv(1024)
            states = json.loads(data.decode())

            ''' --- Process received data --- '''
            names = list(states.keys())
            agent_names = names[:4]
            actions = [0]*len(agent_names)

            ''' --- Ontology based state distirbution --- '''
            brightness_state, temperature_state = state_preprocessing(states, N_LEVEL)

            # print(f'states: {states}')
            # print(f'brightness_state: {brightness_state}')
            # print(f'temperature_state: {temperature_state}')

            ''' --- Select action and send action data --- '''
            actions[0] = int(light1.get_action(brightness_state))
            actions[1] = int(light2.get_action(brightness_state))
            actions[2] = int(roller.get_action(brightness_state))
            actions[3] = int(heater.get_action(temperature_state))

            action_dict = dict(map(lambda x, y: (x, y), agent_names, actions))
            #print(action_dict)
            #print('------------------------')
            action_dict_json = json.dumps(action_dict)
            client_socket.sendall(action_dict_json.encode())

            ''' --- receive thwe next state --- '''
            data = client_socket.recv(1024)
            next_state = json.loads(data.decode())
            next_brightness_state, next_temperature_state = state_preprocessing(next_state, N_LEVEL)

            ''' --- Stack the replay memory --- '''
            
            for name in action_dict.keys():
                if states[name] == next_state[name]:
                    agent = list(filter(lambda x: x.name == name, agents))[0]
                    if action_dict[name] != 0:
                        if name != 'RoomHeater':
                            agent.memory.append([brightness_state[:], action_dict[name], next_brightness_state[:]])
                        else:
                            agent.memory.append([temperature_state[:], action_dict[name], next_temperature_state[:]])
                    action_dict[name] = 0

            # print(f'actions: {actions}')
            # print(f'action_dict: {action_dict}')
            # print(f'action_dict_val: {list(action_dict.values())}')
            light1.memory.append([brightness_state[:], action_dict['RoomLight1'], next_brightness_state[:]])
            light2.memory.append([brightness_state[:], action_dict['RoomLight2'], next_brightness_state[:]])
            roller.memory.append([brightness_state[:], action_dict['RoomRoller'], next_brightness_state[:]])
            heater.memory.append([temperature_state[:], action_dict['RoomHeater'], next_temperature_state[:]])
            
            # state_distance = sum(list(map(lambda x, y: (x-y)**2, list(states.values())[:4], list(next_state.values())[:4])))
            # if state_distance < 0.0005:
            #     break
            if sum(action_dict.values()) == 0:
                break

            for i, action in enumerate(action_dict.values()):
                if action != 0:
                    actions_cnt[i] += 1


        ''' Exit the Home I/O controller process '''
        client_socket.recv(1024)
        train_flag = 'train'
        client_socket.sendall(train_flag.encode())

        data = client_socket.recv(1024)
        final_state = json.loads(data.decode())
        data = client_socket.recv(1024)
        user_cnt = json.loads(data.decode())['user_cnt']

        final_brightness_state, final_temperature_state = state_preprocessing(final_state, N_LEVEL)

        light1.train_model_from_memory(light1.memory, final_brightness_state, user_cnt[0])
        light2.train_model_from_memory(light2.memory, final_brightness_state, user_cnt[1])
        roller.train_model_from_memory(roller.memory, final_brightness_state, user_cnt[2])
        heater.train_model_from_memory(heater.memory, final_temperature_state, user_cnt[3])

        print(actions_cnt)
        f.write(','.join(list(map(lambda x: str(x), actions_cnt))))
        f.write('\n')

    
    client_socket.recv(1024)
    quit_flag = 'quit'
    client_socket.sendall(quit_flag.encode())
    client_socket.close()
    f.close()
    if save_flag == True:
        for agent in agents:
            agent.save_model(WEIGHT_PATH)
    


if __name__ == '__main__':
    for _ in range(3):
        main(load_flag=False, save_flag=False, maximum_episode=200)
        time.sleep(1)
