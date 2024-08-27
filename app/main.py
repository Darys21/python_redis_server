import socket
import threading

def parse_redis_protocol(data):
    """
    Parses RESP (REdis Serialization Protocol) messages.
    Returns a list of commands and their arguments.
    """
    commands = []
    i = 0
    while i < len(data):
        if data[i] == '*':
            i += 1
            num_elements = int(data[i:data.index('\r\n', i)])
            i = data.index('\r\n', i) + 2
            command = []
            for _ in range(num_elements):
                if data[i] == '$':
                    i += 1
                    length = int(data[i:data.index('\r\n', i)])
                    i = data.index('\r\n', i) + 2
                    command.append(data[i:i+length])
                    i += length + 2
            commands.append(command)
        else:
            break
    return commands

def handle_client(conn, addr):
    print(f"Connection established with {addr}")
    pong_message = "+PONG\r\n"
        
    with conn:
        while True:
            client_message = conn.recv(1024)
            if not client_message:
                break

            messages = parse_redis_protocol(client_message.decode())
            for message in messages:
                if len(message) == 0:
                    continue
                
                command = message[0].upper()
                if command == "PING":
                    pong_message = "+PONG\r\n"
                    conn.sendall(pong_message.encode())
                    print(f"Received command: {message}")
                    print(f"Sent response: {pong_message}")
                elif command == "ECHO" and len(message) == 2:
                    response = f"${len(message[1])}\r\n{message[1]}\r\n"
                    conn.sendall(response.encode())
                    print(f"Received command: {message}")
                    print(f"Sent response: {response}")
                else:
                    print(f"Received unknown command: {message}")
def start_server():
    print("Starting server...")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server started and listening on port 6379")
    
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
