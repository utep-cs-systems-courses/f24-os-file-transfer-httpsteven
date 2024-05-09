#!/usr/bin/env python3

import os
import socket
import sys

def initialize_client(address='127.0.0.1', port=25565):
    """Initialize a TCP client socket and connect to the specified server."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((address, port))
        print(f"Connected to the server at {address}:{port}.")
        return client_socket
    except socket.error as e:
        sys.stderr.write(f"Error: Unable to connect to server - {e}\n")
        sys.exit(1)

def transmit_file(client_socket, file_path):
    """Read and send a file to the server via the connected client socket."""
    try:
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as file:
            file_content = file.read()

        file_name_len = str(len(file_name)).zfill(4)
        file_content_len = str(len(file_content)).zfill(8)

        print(f"Sending file: {file_name}")

        client_socket.send(file_name_len.encode())
        client_socket.send(file_name.encode())
        client_socket.send(file_content_len.encode())
        client_socket.send(file_content)
    except Exception as e:
        sys.stderr.write(f"Error: Unable to send file '{file_path}' - {e}\n")

def transmit_multiple_files(client_socket, file_paths):
    """Send multiple files to the server via the connected client socket."""
    file_count = str(len(file_paths)).zfill(4)
    print(f"Preparing to send {len(file_paths)} files.")

    client_socket.send(file_count.encode())

    for file_path in file_paths:
        transmit_file(client_socket, file_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <file1> [<file2> ...]")
        sys.exit(1)

    # Initialize the client connection
    client_socket = initialize_client()
    
    # Get file paths from command-line arguments
    file_paths = sys.argv[1:]

    # Send all specified files to the server
    transmit_multiple_files(client_socket, file_paths)

    # Close the client socket after sending the files
    client_socket.shutdown(socket.SHUT_WR)
    client_socket.close()

    print("File transfer complete.")

if __name__ == "__main__":
    main()
