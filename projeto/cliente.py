
import socket
import configparser

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
            
             # Exibir o tamanho do arquivo recebido em bytes
            file_size = len(received_data)
            print(f"Received the complete file {arquivo} of size {file_size} bytes")

            # Enviar a confirmação (ACK) com o número de bytes recebidos no formato desejado
            ack_message = f"ftcp_ack,{file_size}".encode()
            tcp_sock.sendall(ack_message)
            print(f"Sent acknowledgment: ftcp_ack,{file_size} bytes")
    except Exception as e:
        print(f"Error receiving file: {e}")

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
    
    # Permitir que o cliente escolha entre a.txt e b.txt
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
