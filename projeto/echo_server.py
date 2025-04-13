
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
    try:
        # Receber o comando get
        data = conn.recv(BUFFER_SIZE)
        if not data:
            return
            
        command = data.decode('utf-8')
        print(f"TCP Received from {addr}: {command}")
        
        # Verificar se é um comando get válido
        if command.startswith("get"):
            parts = command.split(',')
            if len(parts) != 2:
                conn.sendall(b"ERROR: Invalid command format")
                return
                
            _, arquivo = parts
            
            # Verificar qual arquivo enviar
            if arquivo == FILE_A and os.path.exists(FILE_A):
                with open(FILE_A, 'rb') as f:
                    file_data = f.read()
                    conn.sendall(file_data)
                print(f"Sent file {arquivo} ({len(file_data)} bytes) to {addr}")
            elif arquivo == FILE_B and os.path.exists(FILE_B):
                with open(FILE_B, 'rb') as f:
                    file_data = f.read()
                    conn.sendall(file_data)
                print(f"Sent file {arquivo} ({len(file_data)} bytes) to {addr}")
            else:
                conn.sendall(b"ERROR: File not found")
                return
        else:
            conn.sendall(b"ERROR: Unknown command")
            return
            
        # Fecha apenas o canal de envio e mantém o canal de recebimento aberto
        conn.shutdown(socket.SHUT_WR)
        
        # Aguardar confirmação do cliente (ACK)
        ack_data = conn.recv(BUFFER_SIZE)
        if ack_data:
            ack_message = ack_data.decode('utf-8')
            print(f"Received ACK from {addr}: {ack_message}")
            
            # Verificar se o ACK contém o número correto de bytes
            if ack_message.startswith("ftcp_ack"):
                parts = ack_message.split(',')
                if len(parts) == 2:
                    bytes_received = int(parts[1])
                    print(f"Client confirmed receipt of {bytes_received} bytes")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
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
