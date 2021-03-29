#!/usr/bin/env python3

import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 7500        # The port used by the server

chan = sys.argv[1]
char = sys.argv[2]
numb = sys.argv[3]
name = sys.argv[4]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(f'{chan},{char},{numb},{name}'.encode())
