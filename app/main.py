import socket
import threading
import time
import sys
import argparse

def parse_redis_protocol(data):
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

def handle_client(conn, addr, data_store, expiry_store, config_params):
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
                elif command == "SET":
                    key = message[1]
                    value = message[2]
                    expiry = None
                    if len(message) == 5 and message[3].upper() == "PX":
                        expiry = int(message[4]) / 1000  # Convert milliseconds to seconds
                    data_store[key] = value
                    if expiry is not None:
                        expiry_store[key] = time.time() + expiry
                    response = "+OK\r\n"
                    conn.sendall(response.encode())
                    print(f"Received command: {message}")
                    print(f"Sent response: {response}")
                elif command == "GET" and len(message) == 2:
                    key = message[1]
                    value = data_store.get(key, None)
                    if key in expiry_store and time.time() > expiry_store[key]:
                        value = None
                        del data_store[key]
                        del expiry_store[key]
                    if value is not None:
                        response = f"${len(value)}\r\n{value}\r\n"
                    else:
                        response = "$-1\r\n"
                    conn.sendall(response.encode())
                    print(f"Received command: {message}")
                    print(f"Sent response: {response}")
                elif command == "CONFIG" and len(message) == 3 and message[1].upper() == "GET":
                    param = message[2]
                    if param in config_params:
                        value = config_params[param]
                        response = f"*2\r\n${len(param)}\r\n{param}\r\n${len(value)}\r\n{value}\r\n"
                    else:
                        response = "*0\r\n"
                    conn.sendall(response.encode())
                    print(f"Received command: {message}")
                    print(f"Sent response: {response}")
                else:
                    print(f"Received unknown command: {message}")

def start_server(dir_path, dbfilename):
    print("Starting server...")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server started and listening on port 6379")
    
    data_store = {}
    expiry_store = {}
    config_params = {
        "dir": dir_path,
        "dbfilename": dbfilename
    }
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, data_store, expiry_store, config_params))
        client_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a Redis-like server with RDB persistence configuration.")
    parser.add_argument("--dir", required=True, help="The directory where the RDB file is stored.")
    parser.add_argument("--dbfilename", required=True, help="The name of the RDB file.")
    args = parser.parse_args()

    start_server(args.dir, args.db)
