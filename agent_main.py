import socket
import json
from RL.agent import *
import os

HOST = '127.0.0.1'
PORT = 55665

BRIGHTNESS_N_STATE = 5
TEMPERATURE_N_STATE = 3
N_ACTION = 3
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
WEIGHT_PATH = CURRENT_PATH+'/weight/'


def state_preprocessing(states):
    brightness_env = list(filter(lambda x: 'Brightness' in x[0], states.items()))
    temperature_env = list(filter(lambda x: 'Temperature' in x[0], states.items()))
    brightness_env_state = list(map(lambda x: min(max(x[1], 0), 10)/10, brightness_env)) # clip (0 ~ 10)/10
    temperature_env_state = list(map(lambda x: (min(max(x[1], -10), 30)+10)/40, temperature_env)) # (clip (-10, 30)+10)/40

    brightness_agent_state = list(map(lambda x: (x[1])/10, states.items()))[:3]
    temperature_agent_state = [states['RoomHeater']/10]

    brigthness_state = brightness_agent_state + brightness_env_state
    temperature_state = temperature_agent_state + temperature_env_state
    return brigthness_state, temperature_state

def pretraining(light1, light2, roller, heater, client_socket, max_iteration):
    ''' --- initialization --- '''
    agents = [light1, light2, roller, heater]
    for agent in agents:
        agent.learning_rate = 0.3

    
    for i in range(max_iteration):
        print(f'Pretraining [{i+1}] ---------------')
        ''' --- State data recived --- '''
        data = client_socket.recv(1024)
        states = json.loads(data.decode())

        ''' --- Process recived data --- '''
        names = list(states.keys())
        agent_names = names[:4]
        actions = [0]*len(agent_names)

        ''' --- Ontology based state distirbution --- '''
        brightness_state, temperature_state = state_preprocessing(states)
        
        print(f'brigthness_state: {brightness_state}')
        print(f'temperature_state: {temperature_state}')

        actions[0] = int(light1.get_action(brightness_state))
        actions[1] = int(light2.get_action(brightness_state))
        actions[2] = int(roller.get_action(brightness_state))
        actions[3] = int(heater.get_action(temperature_state))

        rewards = list(map(lambda x: 1 if x==0 else -1, actions))

        action_dict = dict(map(lambda x, y: (x, y), agent_names, actions))
        print(action_dict)
        print(rewards)
        print('------------------------')
        action_dict_json = json.dumps(action_dict)
        client_socket.sendall(action_dict_json.encode())

        data = client_socket.recv(1024)
        next_state = json.loads(data.decode())
        next_brightness_state, next_temperature_state = state_preprocessing(next_state)

        light1.train_model(brightness_state, actions[0], rewards[0], next_brightness_state, False)
        light2.train_model(brightness_state, actions[1], rewards[1], next_brightness_state, False)
        roller.train_model(brightness_state, actions[2], rewards[2], next_brightness_state, False)
        heater.train_model(next_temperature_state, actions[3], rewards[3], next_temperature_state, False)

    for agent in agents:
        agent.learning_rate = 0.001
        agent.save_model(WEIGHT_PATH)


def main(load_flag=False, pretrain_flag=True, pretrain_iteration=300):
    ''' --- Socket setup --- '''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    ''' --- Agent setup --- '''
    light1 = IoTAgent(BRIGHTNESS_N_STATE, N_ACTION, 'RoomLight1')
    light2 = IoTAgent(BRIGHTNESS_N_STATE, N_ACTION, 'RoomLight2')
    roller = IoTAgent(BRIGHTNESS_N_STATE, N_ACTION, 'RoomRoller')
    heater = IoTAgent(TEMPERATURE_N_STATE, N_ACTION, 'RoomHeater')

    ''' load or pretrain the model'''
    if load_flag == True:
        light1.load_model(WEIGHT_PATH)
        light2.load_model(WEIGHT_PATH)
        roller.load_model(WEIGHT_PATH)
        heater.load_model(WEIGHT_PATH)

    if pretrain_flag == True:
        pretraining(light1, light2, roller, heater, client_socket, pretrain_iteration)
        print('Pretraining is finished --------------------- ')

    for _ in range(10):
        ''' --- State data received --- '''
        data = client_socket.recv(1024)
        states = json.loads(data.decode())

        ''' --- Process received data --- '''
        names = list(states.keys())
        agent_names = names[:4]
        actions = [0]*len(agent_names)

        ''' --- Ontology based state distirbution --- '''
        brightness_state, temperature_state = state_preprocessing(states)

        print(f'brigthness_state: {brightness_state}')
        print(f'temperature_state: {temperature_state}')

        ''' --- Select action and send action data --- '''
        actions[0] = int(light1.get_action(brightness_state))
        actions[1] = int(light2.get_action(brightness_state))
        actions[2] = int(roller.get_action(brightness_state))
        actions[3] = int(heater.get_action(temperature_state))

        action_dict = dict(map(lambda x, y: (x, y), agent_names, actions))
        print(action_dict)
        print('------------------------')
        action_dict_json = json.dumps(action_dict)
        client_socket.sendall(action_dict_json.encode())

        ''' --- receive the next state --- '''
        data = client_socket.recv(1024)
        next_state = json.loads(data.decode())
        next_brightness_state, next_temperature_state = state_preprocessing(next_state)

    ''' Exit the Home I/O controller process '''
    client_socket.recv(1024)
    quit_flag = 'quit'
    client_socket.sendall(quit_flag.encode())
    client_socket.close()


if __name__ == '__main__':
    main(load_flag=False, pretrain_flag=True, pretrain_iteration=300)
