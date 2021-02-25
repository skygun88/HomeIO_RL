import socket
import json
from agent import iot

HOST = '127.0.0.1'
PORT = 55665

BRIGHTNESS_N_STATE = 5
TEMPERATURE_N_STATE = 3
N_ACTION = 3

def main():
    ''' --- Socket setup --- '''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))


    ''' --- Agent setup --- '''
    light1 = iot.IoTAgent(BRIGHTNESS_N_STATE, N_ACTION)
    light2 = iot.IoTAgent(BRIGHTNESS_N_STATE, N_ACTION)
    roller = iot.IoTAgent(BRIGHTNESS_N_STATE, N_ACTION)
    heater = iot.IoTAgent(TEMPERATURE_N_STATE, N_ACTION)

    for _ in range(10):
        ''' --- State data recived --- '''
        data = client_socket.recv(1024)
        data = json.loads(data.decode())

        print('--- recived data ---')
        for key, val in data.items():
            print(f'{key}: {val}')
        print('--------------------')

        ''' --- Process recived data --- '''
        names = list(data.keys())
        agent_names = names[:4]
        actions = [0]*len(agent_names)

        ''' --- Ontology based state distirbution --- '''
        brightness_env = list(filter(lambda x: 'Brightness' in x[0], data.items()))
        temperature_env = list(filter(lambda x: 'Temperature' in x[0], data.items()))
        brightness_env_state = list(map(lambda x: min(max(x[1], 0), 10)/10, brightness_env)) # clip (0 ~ 10)/10
        temperature_env_state = list(map(lambda x: (min(max(x[1], -10), 30)+10)/40, temperature_env)) # (clip (-10, 30)+10)/40

        brightness_agent_state = list(map(lambda x: (x[1])/10, data.items()))[:3]
        temperature_agent_state = [data['RoomHeater']/10]

        brigthness_state = brightness_agent_state + brightness_env_state
        temperature_state = temperature_agent_state + temperature_env_state

        print(f'brigthness_state: {brigthness_state}')
        print(f'temperature_state: {temperature_state}')

        # print(data[names[0]])
        actions[0] = int(light1.get_action(brigthness_state))
        actions[1] = int(light2.get_action(brigthness_state))
        actions[2] = int(roller.get_action(brigthness_state))
        actions[3] = int(heater.get_action(temperature_state))

        print(actions)

        '''
        if data[names[0]] >= 10.0:
            actions[0] = 2
        else:
            actions[0] = 1
        '''

        action_dict = dict(map(lambda x, y: (x, y), agent_names, actions))
        print(action_dict)
        action_dict_json = json.dumps(action_dict)
        client_socket.sendall(action_dict_json.encode())




    # 소켓을 닫습니다.
    client_socket.close()


if __name__ == '__main__':
    main()

# a = {'a': 1, 'b': 2}
# a_json = json.dumps(a)
# new_a = json.loads(a_json)
# print(a, type(a))
# print(a_json, type(a_json))
# print(new_a, type(new_a))