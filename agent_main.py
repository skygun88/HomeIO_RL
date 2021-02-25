import socket
import json

HOST = '127.0.0.1'
PORT = 55665

def main():
    ''' --- Socket setup --- '''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

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

    brightness_env = list(filter(lambda x: 'Brightness' in x[0], data.items()))
    temperature_env = list(filter(lambda x: 'Temperature' in x[0], data.items()))
    brightness_state = list(map(lambda x: x[1], brightness_env))
    tempearture_state = list(map(lambda x: x[1], temperature_env))



    # print(data[names[0]])
    if data[names[0]] >= 10.0:
        actions[0] = 2
    else:
        actions[0] = 1

    action_dict = dict(map(lambda x, y: (x, y), names, actions))
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