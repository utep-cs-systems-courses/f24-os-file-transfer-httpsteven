#! /usr/bin/env python3

import os
import socket
import select
import sys

TRANSFERRED_FOLDER = "transferred-files"

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 25565))
    server_socket.listen(5)
    print("Server started. Waiting for connections...")
    return server_socket

def accept_connection(server_socket):
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")
    return client_socket

def receive_file(client_socket):
    try:
        file_count = int(client_socket.recv(4).decode())
        print(f"Receiving {file_count} files...")

        for _ in range(file_count):
            file_name_len = int(client_socket.recv(4).decode())
            file_name = client_socket.recv(file_name_len).decode()
            file_content_len = int(client_socket.recv(8).decode())
            file_content = client_socket.recv(file_content_len)

            print(f"Received file: {file_name}")

            save_file(file_name, file_content)

    except ValueError:
        print("Error: Invalid data received. Expected an integer.")
    except Exception as e:
        print(f"Error: {str(e)}")
        
def save_file(file_name, file_content):
    file_path = os.path.join(TRANSFERRED_FOLDER, file_name)

    if os.path.exists(file_path):
        print(f"File {file_name} already exists. Deleting old file.")
        os.remove(file_path)

    with open(file_path, "wb") as file:
        file.write(file_content)

def main():
    os.makedirs(TRANSFERRED_FOLDER, exist_ok=True)

    server_socket = start_server()
    sockets = [server_socket]

    while True:
        readable, _, _ = select.select(sockets, [], [])

        for sock in readable:
            if sock == server_socket:
                client_socket = accept_connection(server_socket)
                sockets.append(client_socket)
                
                # Fork off a child process
                pid = os.fork()
                
                if pid == 0:  # This is the child process
                    server_socket.close()  # Child process doesn't need the server socket
                    receive_file(client_socket)
                    client_socket.close()
                    sys.exit(0)
            else:
                # Parent process continues waiting for connections
                pass
        
        # Reap zombie child processes
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
            except OSError:
                break

if __name__ == "__main__":
    main()
