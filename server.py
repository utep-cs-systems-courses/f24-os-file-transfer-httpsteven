#!/usr/bin/env python3

import os
import socket
import select
import sys

TRANSFERRED_FOLDER = "transferred-files"

def initialize_server(address="127.0.0.1", port=25565, backlog=5):
    """Set up and return a server socket ready to accept client connections."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((address, port))
        server_socket.listen(backlog)
        print(f"Server started on {address}:{port}. Waiting for connections...")
        return server_socket
    except socket.error as e:
        sys.stderr.write(f"Error: Unable to start server - {e}\n")
        sys.exit(1)

def accept_new_connection(server_socket):
    """Accept a new client connection on the server socket."""
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        return client_socket
    except socket.error as e:
        sys.stderr.write(f"Error: Unable to accept connection - {e}\n")

def receive_files_from_client(client_socket):
    """Receive multiple files from a connected client socket."""
    try:
        file_count = int(client_socket.recv(4).decode())
        print(f"Receiving {file_count} files...")

        for _ in range(file_count):
            file_name_length = int(client_socket.recv(4).decode())
            file_name = client_socket.recv(file_name_length).decode()
            file_content_length = int(client_socket.recv(8).decode())
            file_content = b""

            # Receive the file content in chunks to handle larger files
            remaining_bytes = file_content_length
            while remaining_bytes > 0:
                chunk = client_socket.recv(min(remaining_bytes, 4096))
                if not chunk:
                    break
                file_content += chunk
                remaining_bytes -= len(chunk)

            print(f"Received file: {file_name}")
            save_file(file_name, file_content)

    except ValueError:
        sys.stderr.write("Error: Invalid data received. Expected an integer.\n")
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")

def save_file(file_name, file_content):
    """Save the received file content to disk in the transferred folder."""
    try:
        file_path = os.path.join(TRANSFERRED_FOLDER, file_name)

        if os.path.exists(file_path):
            print(f"File {file_name} already exists. Deleting old version.")
            os.remove(file_path)

        with open(file_path, "wb") as file:
            file.write(file_content)
    except Exception as e:
        sys.stderr.write(f"Error saving file {file_name}: {e}\n")

def handle_connections(server_socket):
    """Manage incoming client connections using a select loop."""
    sockets = [server_socket]

    while True:
        readable, _, _ = select.select(sockets, [], [])

        for sock in readable:
            if sock == server_socket:
                client_socket = accept_new_connection(server_socket)
                if client_socket:
                    sockets.append(client_socket)
                    pid = os.fork()
                    if pid == 0:  # Child process
                        server_socket.close()  # Child doesn't need server socket
                        receive_files_from_client(client_socket)
                        client_socket.close()
                        sys.exit(0)
            else:
                pass  # The parent process continues waiting for connections

        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
            except OSError:
                break

def main():
    os.makedirs(TRANSFERRED_FOLDER, exist_ok=True)

    server_socket = initialize_server()
    handle_connections(server_socket)

if __name__ == "__main__":
    main()
