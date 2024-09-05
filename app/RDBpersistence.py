import argparse
import socket

def handle_config_get(parameter, value):
    """
    Returns a RESP formatted string for the CONFIG GET command.

    Args:
        parameter (str): The configuration parameter name.
        value (str): The configuration parameter value.

    Returns:
        str: A RESP formatted string containing the parameter name and value.
    """
    return f"*2\r\n${len(parameter)}\r\n{parameter}\r\n${len(value)}\r\n{value}\r\n"
def main():
    """
    Main function of the RDB Persistence Extension server.
    """
    parser = argparse.ArgumentParser(description='RDB Persistence Extension')
    parser.add_argument('--dir', type=str, help='Directory containing the RDB files', default='/')
    parser.add_argument('--dbfilename', type=str, help='Name of the RDB file to load')
    parser.add_argument('--port', type=int, help='Port to bind', default=6379)
    args = parser.parse_args()

        
    print(args.dir)
    print(args.dbfilename)
    print(args.port)
    # Store the configuration in a dictionary
    config = {
        'dir': args.dir,
        'dbfilename': args.dbfilename
    }

    # Create a socket to listen for connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6379))
    server_socket.listen(1)
    print("RDB Persistence Extension started. Listening on localhost:6379")
    
    while True:
        # Accept a connection from a client
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Receive data from the client
        data = client_socket.recv(1024).decode()
        if data.startswith('CONFIG GET'):
            # Split the data into command and parameter
            command, parameter = data.split(' ', 1)
            if parameter in config:
                # Handle the CONFIG GET command
                response = handle_config_get(parameter, config[parameter])
                client_socket.sendall(response.encode())
            else:
                # Handle unknown parameter
                client_socket.sendall("$-1\r\n".encode())
                client_socket.close()
        else:
            # Handle non-CONFIG GET command
            client_socket.sendall("$-1\r\n".encode())
            client_socket.close()
                
if __name__ == '__main__':
    main()