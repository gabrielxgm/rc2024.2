import socket
import threading
import configparser

# Carregar configurações
config = configparser.ConfigParser()
config.read('config.ini')

TCP_PORT = int(config['SERVER_CONFIG']['TCP_PORT'])
FILE_A = config['SERVER_CONFIG']['FILE_A']
FILE_B = config['SERVER_CONFIG']['FILE_B']

def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")
    with conn:
        # Recebe o nome do arquivo primeiro (até encontrar \n)
        buffer = b''
        while b'\n' not in buffer:
            byte = conn.recv(1)
            if not byte:
                print("Conexão encerrada antes do nome do arquivo ser enviado.")
                return
            buffer += byte
        filename = buffer.decode('utf-8').strip()

        # Valida nome de arquivo permitido
        if filename not in [FILE_A, FILE_B]:
            print(f"Nome de arquivo não permitido: {filename}")
            conn.close()
            return

        print(f"Salvando conteúdo no arquivo: {filename}")
        with open(filename, 'wb') as f_out:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"TCP Received from {addr}: {data.decode('utf-8', errors='ignore')}")
                f_out.write(data)
                conn.sendall(data)
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
    tcp_thread = threading.Thread(target=tcp_echo)
    tcp_thread.daemon = True
    tcp_thread.start()

    print("Servidor rodando. Pressione Ctrl+C para encerrar.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Servidor encerrado.")
