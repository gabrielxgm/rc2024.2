import socket
import configparser

# Carregar configurações
config = configparser.ConfigParser()
config.read('config.ini')

TCP_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])
FILE_A = config['SERVER_CONFIG']['FILE_A']
FILE_B = config['SERVER_CONFIG']['FILE_B']

print("Escolha o arquivo para enviar:")
print("1 -", FILE_A)
print("2 -", FILE_B)

escolha = input("Digite 1 ou 2: ").strip()
if escolha == '1':
    arquivo_escolhido = FILE_A
elif escolha == '2':
    arquivo_escolhido = FILE_B
else:
    print("Opção inválida.")
    exit(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', TCP_PORT))
    print(f"Conectado ao servidor. Enviando {arquivo_escolhido}...")

    # Enviar o nome do arquivo (codificado) seguido de um separador especial
    s.sendall((arquivo_escolhido + '\n').encode('utf-8'))

    # Enviar o conteúdo
    with open(arquivo_escolhido, 'rb') as f:
        content = f.read()
        s.sendall(content)

    s.shutdown(socket.SHUT_WR)

    with open("eco_" + arquivo_escolhido, 'wb') as f:
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)

    print(f"Resposta salva em eco_{arquivo_escolhido}")

