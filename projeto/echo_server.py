
import socket
import threading
import configparser
import os

# Carregar configurações do arquivo config.ini
config = configparser.ConfigParser()
config.read('config.ini')

TCP_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])
UDP_NEGOTIATION_PORT = int(config['SERVER_CONFIG']['UDP_NEGOTIATION_PORT'])
FILE_A = config['SERVER_CONFIG']['FILE_A']
FILE_B = config['SERVER_CONFIG']['FILE_B']
BUFFER_SIZE = 1024

def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")
    with conn:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            return
        command, arquivo = data.decode().split(',')
        if command == "get":
            print(f"Client requested file: {arquivo}")
            if arquivo == FILE_A or arquivo == FILE_B:
                send_file(conn, arquivo)
            else:
                print("Requested file does not exist.")
                conn.sendall(b"ERROR,File not found")
        else:
            print("Invalid command received.")
    print(f"TCP Client disconnected from {addr}")
def send_file(conn, arquivo):
    try:
        # Abrir e enviar o arquivo solicitado
        with open(arquivo, 'rb') as f:
            while (chunk := f.read(BUFFER_SIZE)):
                conn.sendall(chunk)
        print(f"Sent the complete file {arquivo}")

        # Enviar a confirmação de ACK após a transferência do arquivo
        file_size = os.path.getsize(arquivo)


        # Enviar o arquivo ao cliente
        print(f"Sent file: {file_size} bytes")
    except Exception as e:
        print(f"Error sending file: {e}")
        conn.sendall(b"ERROR,File transfer failed")

def tcp_echo():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('0.0.0.0', TCP_PORT))
    tcp_sock.listen(5)
    print(f"TCP server listening on port {TCP_PORT}")
    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(target=handle_tcp_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

def udp_negotiation():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', UDP_NEGOTIATION_PORT))
    print(f"UDP server listening on port {UDP_NEGOTIATION_PORT}")
    while True:
        data, addr = udp_sock.recvfrom(BUFFER_SIZE)
        if not data:
            continue
        print(f"UDP Received from {addr}: {data.decode()}")
        comando, protocolo, arquivo = data.decode().split(',')
        if comando == "REQUEST" and protocolo == "TCP":
            if arquivo in [FILE_A, FILE_B]:
                # Responde com a porta TCP para o arquivo solicitado
                response = f"RESPONSE,TCP,{TCP_PORT},{arquivo}"
            else:
                # Responde com erro se o arquivo não existir
                response = "ERROR,PROTOCOLO INVALIDO,,"

            udp_sock.sendto(response.encode(), addr)

if __name__ == "__main__":
    # Iniciar threads para UDP e TCP
    udp_thread = threading.Thread(target=udp_negotiation)
    udp_thread.daemon = True
    udp_thread.start()

    tcp_thread = threading.Thread(target=tcp_echo)
    tcp_thread.daemon = True
    tcp_thread.start()

    print("Servidor rodando. Pressione Ctrl+C para encerrar.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Servidor encerrado.")

'''import socket
import threading
import configparser

# Carregar configurações
config = configparser.ConfigParser()
config.read('config.ini')

UDP_NEGOTIATION_PORT = int(config['SERVER_CONFIG']['UDP_NEGOTIATION_PORT'])
TCP_TRANSFER_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])
BUFFER_SIZE = 1024

def handle_tcp_connection(conn, addr):
    try:
        print(f"Conexão TCP de {addr}")
        request = conn.recv(BUFFER_SIZE).decode()
        print(f"Requisição recebida: {request}")

        if request.startswith("get,"):
            filename = request.split(",")[1]

            try:
                with open(filename, "rb") as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        conn.sendall(chunk)
                print(f"Arquivo '{filename}' enviado com sucesso.")

                # Esperar o ACK do cliente após o envio do arquivo
                ack = conn.recv(BUFFER_SIZE).decode()
                print(f"ACK recebido do cliente: {ack}")

            except FileNotFoundError:
                conn.sendall(b"Erro: Arquivo nao encontrado.")
                print(f"Erro: Arquivo '{filename}' nao encontrado.")

    except Exception as e:
        print(f"Erro na conexao TCP: {e}")
    finally:
        conn.close()
        print(f"Conexão TCP encerrada com {addr}")

def start_server():
    # Inicia socket UDP para negociação
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", UDP_NEGOTIATION_PORT))
    print(f"Servidor UDP escutando na porta {UDP_NEGOTIATION_PORT}...")

    # Inicia socket TCP para transferência
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(("0.0.0.0", TCP_TRANSFER_PORT))
    tcp_sock.listen(5)
    print(f"Servidor TCP aguardando conexões na porta {TCP_TRANSFER_PORT}...")

    while True:
        # Receber solicitação via UDP
        data, addr = udp_sock.recvfrom(BUFFER_SIZE)
        message = data.decode()
        print(f"Solicitação UDP recebida de {addr}: {message}")

        if message.startswith("REQUEST,TCP,"):
            parts = message.split(",")
            filename = parts[2]

            response = f"RESPONSE,TCP,{TCP_TRANSFER_PORT},{filename}"
            udp_sock.sendto(response.encode(), addr)
            print(f"Resposta enviada para {addr}: {response}")

            # Aceitar conexão TCP em paralelo
            conn, tcp_addr = tcp_sock.accept()
            threading.Thread(target=handle_tcp_connection, args=(conn, tcp_addr)).start()

if __name__ == "__main__":
    start_server()'''
