#! /usr/bin/env python3

import os
import socket
import sys

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 25565))
    print("Connected to the server.")
    return client_socket

def send_file(client_socket, file_path):
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

def send_files(client_socket, files):
    file_count = str(len(files)).zfill(4)
    print(f"Sending {file_count} files...")

    client_socket.send(file_count.encode())

    for file_path in files:
        send_file(client_socket, file_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <file1> [<file2> ...]")
        sys.exit(1)

    client_socket = start_client()
    files = sys.argv[1:]
    
    send_files(client_socket, files)

    client_socket.shutdown(socket.SHUT_WR)
    client_socket.close()

    print("File transfer complete.")

if __name__ == "__main__":
    main()
