
import socket
import configparser

# Carregar configurações do arquivo config.ini
config = configparser.ConfigParser()
config.read('config.ini')

SERVER_ADDRESS = ('127.0.0.1', int(config['SERVER_CONFIG']['UDP_NEGOTIATION_PORT']))
BUFFER_SIZE = 1024
TCP_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])

"""
Envia uma solicitação de negociação para o servidor via UDP.

Parametros:
    comando (str): O comando a ser enviado (nesta etapa, sempre "REQUEST").
    protocolo (str): O protocolo de transferência desejado.
    arquivo (str): O nome do arquivo a ser solicitado.
"""
def send_request(comando, protocolo, arquivo):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.settimeout(5)  # Defina um tempo de espera para a resposta
            udp_sock.sendto(f"{comando},{protocolo},{arquivo}".encode(), SERVER_ADDRESS)
            print(f"Sent: {comando},{protocolo},{arquivo}")
            data, server = udp_sock.recvfrom(BUFFER_SIZE)
            print(f"Received: {data.decode()}")
            if data.startswith(b"RESPONSE"):
                transfer_port = int(data.decode().split(",")[2])
                print(f"Server response: {data.decode()}")
                # Estabelecer a conexão TCP para receber o arquivo
                receive_file(transfer_port, arquivo)
            else:
                print(f"Error: {data.decode()}")
    except socket.timeout:
        print("Error: Server response timed out")
    except Exception as e:
        print(f"Error sending request: {e}")


"""
Estabelece uma conexão TCP com o servidor e recebe o arquivo solicitado.

Após receber o arquivo, envia uma confirmação (ACK) para o servidor
com o número total de bytes recebidos.

Parametros:
    transfer_port (int): A porta TCP do servidor para a transferência do arquivo.
    arquivo (str): O nome do arquivo esperado.
"""
def receive_file(transfer_port, arquivo):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.connect(('127.0.0.1', transfer_port))
            print(f"Connected to server on TCP port {transfer_port}")
            tcp_sock.sendall(f"get,{arquivo}".encode())
            print(f"Sent: get,{arquivo}")
            
            received_data = b""
            while True:
                data = tcp_sock.recv(BUFFER_SIZE)
                if not data:
                    break
                received_data += data
            
             # Exibir o tamanho do arquivo recebido em bytes
            file_size = len(received_data)
            print(f"Received the complete file {arquivo} of size {file_size} bytes")

            # Enviar a confirmação (ACK) com o número de bytes recebidos no formato desejado
            ack_message = f"ftcp_ack,{file_size}".encode()
            tcp_sock.sendall(ack_message)
            print(f"Sent acknowledgment: ftcp_ack,{file_size} bytes")
    except Exception as e:
        print(f"Error receiving file: {e}")

"""
Permite ao usuário escolher o protocolo de transferência
"""
def choose_protocol():
    print("Escolha o protocolo de transferencia:")
    print("1 - TCP (recomendado)")
    print("2 - UDP")
    choice = input("Digite o número da sua escolha: ")
    if choice == '1':
        return "TCP"
    elif choice == '2':
        return "UDP"
    else:
        print("Opção inválida. Usando TCP por padrão.")
        return "TCP"

"""
Permite ao usuário escolher o arquivo a ser solicitado do servidor.
"""
def choose_file():
    print("\nEscolha o arquivo que deseja solicitar:")
    print("1 - a.txt")
    print("2 - b.txt")
    print("3 - Outro")
    choice = input("Digite sua escolha (1-3): ")
    
    if choice == '1':
        return "a.txt"
    elif choice == '2':
        return "b.txt"
    elif choice == '3':
        return input("Digite o nome do arquivo: ")
    else:
        print("Opção inválida. Usando a.txt como padrão.")
        return "a.txt"

if __name__ == "__main__":
    comando = "REQUEST"

    protocolo = choose_protocol()
    arquivo = choose_file()

    send_request(comando, protocolo, arquivo)

'''import socket
import configparser

# Carregar configurações do arquivo config.ini
config = configparser.ConfigParser()
config.read('config.ini')

SERVER_ADDRESS = ('127.0.0.1', int(config['SERVER_CONFIG']['UDP_NEGOTIATION_PORT']))
BUFFER_SIZE = 1024

def send_request(comando, protocolo, arquivo):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.settimeout(5)
            udp_sock.sendto(f"{comando},{protocolo},{arquivo}".encode(), SERVER_ADDRESS)
            print(f"Sent: {comando},{protocolo},{arquivo}")
            data, server = udp_sock.recvfrom(BUFFER_SIZE)
            print(f"Received: {data.decode()}")
            if data.startswith(b"RESPONSE"):
                transfer_port = int(data.decode().split(",")[2])
                print(f"Server response: {data.decode()}")

                # Criar o socket TCP e conectar ao servidor
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
                    tcp_sock.connect(('127.0.0.1', transfer_port))
                    print(f"Connected to server on TCP port {transfer_port}")
                    
                    # Enviar solicitação do arquivo
                    tcp_sock.sendall(f"get,{arquivo}".encode())
                    print(f"Sent: get,{arquivo}")

                    # Receber os dados do arquivo
                    receive_file(tcp_sock, arquivo)
            else:
                print(f"Error: {data.decode()}")
    except socket.timeout:
        print("Error: Server response timed out")
    except Exception as e:
        print(f"Error sending request: {e}")

def receive_file(tcp_sock, arquivo):
    try:
        received_data = b""
        while True:
            chunk = tcp_sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            received_data += chunk

        print(f"Arquivo recebido ({len(received_data)} bytes)")

        # Mostrar o conteúdo (opcional - cuidado se for binário)
        try:
            print(f"Conteúdo do arquivo:\n{received_data.decode()}")
        except:
            print("[Aviso] Não foi possível decodificar o conteúdo como texto.")

        # Enviar ACK com tamanho real do arquivo
        ack_message = f"ftcp_ack,{len(received_data)}".encode()
        tcp_sock.sendall(ack_message)
        print(f"Sent acknowledgment: {ack_message.decode()}")

    except Exception as e:
        print(f"Erro ao receber o arquivo: {e}")

def choose_file():
    print("Escolha o arquivo que deseja solicitar:")
    print("1 - a.txt")
    print("2 - b.txt")
    choice = input("Digite o número da sua escolha: ")
    if choice == '1':
        return "a.txt"
    elif choice == '2':
        return "b.txt"
    else:
        print("Opção inválida. Usando o arquivo padrão a.txt.")
        return "a.txt"

if __name__ == "__main__":
    comando = "REQUEST"
    protocolo = "TCP"
    arquivo = choose_file()
    send_request(comando, protocolo, arquivo)'''
