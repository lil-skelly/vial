import argparse
import logging
from rich.logging import RichHandler

import socketserver
import subprocess

import ipaddress
import netifaces

import threading
from time import sleep

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)]
)

log = logging.getLogger("rich")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-H",
    "--host",
    default="eth0",
    type=str,
    help="Host to use when binding the socket"
)

parser.add_argument(
    "-p",
    "--port",
    required=True,
    type=int,
    help="Port to use when binding the socket"
)

args = parser.parse_args()
# Logging format: <LEVEL_INDICATOR> [CLIENT IP] [-> COMMAND] [ERROR]


def check_iface(iface: str):
    try:
        host = ipaddress.IPv4Address(iface)
    except ipaddress.AddressValueError:
        try:
            host = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]["addr"]
        except ValueError:
            log.error(
                "Error detering hosting address. Did you provide a valid [underline]interface[/underline] or [underline]ip[/underline]?"
            )
            exit()

    return host


class Service(socketserver.BaseRequestHandler):
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
        self.request.sendall(data)

    def receive(self) -> str:
        """
        Receive a 4096 bit stripped string from the client
        """
        return self.request.recv(4096).strip().decode("utf-8")

    def handle(self) -> None:
        host, port = self.client_address
        log.info(f"[bold green][+][/] {host}:{port} connected")

        while True:
            command = self.receive()

            if not command.lower() == "quit":
                try:
                    if command != "":
                        log.info(f"[bold blue][*][/] {host}:{port} -> {command}")

                    stderr, stdout = self.run(command)
                    self.send(stderr + stdout)
                except BrokenPipeError as e:
                    log.error(f"{host}:{port} {e}")
                    break
            else:
                self.send("[bold blue][*][/] Received <quit>. Exiting pseudo-shell\n")
                log.info(f"[bold red][-][/] {host}:{port} quitted")

                break


class ThreadedService(
        socketserver.ThreadingTCPServer,
        socketserver.DatagramRequestHandler
):
    pass


def main(args) -> None:
    args.host = check_iface(args.host)

    server = ThreadedService((args.host, args.port), Service)
    server.allow_reuse_address = True

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    host, port = server.server_address
    log.info(f"[bold blue][*][/] Server started on {host}:{port}")

    while (threading.active_count() >= 2):
        sleep(10)


if __name__ == "__main__":
    main(args)
