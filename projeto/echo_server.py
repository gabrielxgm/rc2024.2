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

def udp_echo():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', UDP_NEGOTIATION_PORT))
    print(f"UDP server listening on port {UDP_NEGOTIATION_PORT}")
    while True:
        data, addr = udp_sock.recvfrom(1024)
        if not data:
            continue
        print(f"UDP Received from {addr}: {data.decode('utf-8')}")
        
        # Processar a solicitação REQUEST
        if data.decode().startswith('REQUEST'):
            _, protocolo, arquivo = data.decode().split(',')
            if protocolo == "TCP" and arquivo in [FILE_A, FILE_B]:
                response = f"RESPONSE,TCP,{TCP_PORT},{arquivo}"
            else:
                response = "ERROR,PROTOCOLO INVALIDO,,"
            udp_sock.sendto(response.encode(), addr)

def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"TCP Received from {addr}: {data.decode('utf-8')}")
            # Comando 'get' para solicitar o arquivo
            if data.decode().startswith("get"):
                _, arquivo = data.decode().split(',')
                if arquivo == FILE_A and os.path.exists(FILE_A):
                    with open(FILE_A, 'rb') as f:
                        file_data = f.read()
                        conn.sendall(file_data)
                    print(f"Sent file {arquivo} to {addr}")
                elif arquivo == FILE_B and os.path.exists(FILE_B):
                    with open(FILE_B, 'rb') as f:
                        file_data = f.read()
                        conn.sendall(file_data)
                    print(f"Sent file {arquivo} to {addr}")
                else:
                    conn.sendall(b"ERROR: File not found")
                break

        # Aguardar confirmação do cliente (ACK)
        data = conn.recv(1024)
        if data.decode().startswith("ftcp_ack"):
            print(f"Received ACK: {data.decode()}")
    print(f"TCP Client disconnected from {addr}")

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

if __name__ == '__main__':
    # Iniciar thread para UDP
    udp_thread = threading.Thread(target=udp_echo)
    udp_thread.daemon = True
    udp_thread.start()

    # Iniciar thread para TCP
    tcp_thread = threading.Thread(target=tcp_echo)
    tcp_thread.daemon = True
    tcp_thread.start()

    print("Servidor rodando. Pressione Ctrl+C para encerrar.")

    try:
        # Mantém o programa principal em execução
        while True:
            pass
    except KeyboardInterrupt:
        print("Servidor encerrado.")
