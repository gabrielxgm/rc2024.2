import socket
import configparser

# Carregar configurações
config = configparser.ConfigParser()
config.read('config.ini')

TCP_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])
FILE_A = config['SERVER_CONFIG']['FILE_A']
FILE_B = config['SERVER_CONFIG']['FILE_B']  # caso queira verificar depois

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', TCP_PORT))
    print("Conectado ao servidor.")

    with open(FILE_A, 'rb') as f:
        content = f.read()
        s.sendall(content)
        print("Arquivo a.txt enviado.")

    # Receber resposta (eco)
    with open("eco_" + FILE_B, 'wb') as f:
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)

    print(f"Resposta salva em eco_{FILE_B}")

