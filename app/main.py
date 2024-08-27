import socket

def start_server():
    print("Starting server...")
    
    pong_message = "+PONG\r\n"
    
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server started and listening on port 6379")
    
    while True: 
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        
        with conn:
            while True:
                client_message = conn.recv(1024)
                if not client_message:
                    break
                
                messages = client_message.decode().splitlines()
                for message in messages:
                    if message == "PING":
                        conn.sendall(pong_message.encode())
                        print(f"Received message: {message}")
                        print(f"Sent message: {pong_message}")
                    else:
                        print(f"Received unknown message: {message}")
            
if __name__ == "__main__":
    start_server()