import socket
import configparser
import sys

# Carregar configurações do arquivo config.ini
config = configparser.ConfigParser()
config.read('config.ini')

SERVER_ADDRESS = ('127.0.0.1', int(config['SERVER_CONFIG']['UDP_NEGOTIATION_PORT']))
BUFFER_SIZE = 1024
TCP_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])

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

            file_size = len(received_data)
            print(f"Received the complete file {arquivo} of size {file_size} bytes")

            ack_message = f"ftcp_ack,{file_size}".encode()
            tcp_sock.sendall(ack_message)
            print(f"Sent acknowledgment: ftcp_ack,{file_size} bytes")
    except Exception as e:
        print(f"Error receiving file: {e}")

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cliente_ftcp.py <nome_do_arquivo>")
        sys.exit(1)

    arquivo = sys.argv[1]
    protocolo = choose_protocol()
    comando = "REQUEST"

    send_request(comando, protocolo, arquivo)
