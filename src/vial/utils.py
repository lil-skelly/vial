import vial
from vial.session import decode, sign
from rich.prompt import Prompt as prompt
import json
import requests
import ipaddress
from typing import TypedDict

# NOTE: cookie = sign(json.loads(session_cookie_structure), secret_key, legacy=legacy)


class Proxy(TypedDict):
    http: str
    https: str


def validate_interface(i: str) -> ipaddress.IPv4Address:
    try:
        host = ipaddress.IPv4Address(i)
    except ipaddress.AddressValueError:
        try:
            host = netifaces.ifaddresses(i)[netifaces.AF_INET][0]["addr"]
        except ValueError:
            vial.log.error(
                "Error detering HTTP hosting address. Did you provide an [underline]interface[/underline] or [underline]ip[/underline]?"
            )
        return host


def decode_handler() -> None:
    if not vial.FETCHED_COOKIE:
        cookie = prompt.ask("[bold blue][?][/] Enter the cookie")
    else:
        cookie = vial.FETCHED_COOKIE

    decoded_cookie = decode(cookie)
    vial.log.info(f"Decoded cookie: [bold]{decoded_cookie}[/]")


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
            f"Failed to fetch session data from the server. {_extract_error(e)}",
        )

    vial.log.info(f"Server returned HTTP {resp.status_code} ({resp.reason})")
    cookie = vial.web_session.cookies.get(cookie_name)
    if not cookie:
        return vial.log.error(
            "Failed to fetch session data from the server. Are you sure the url  and cookie name are correct?",
        )
    vial.log.info(f"[bold green][+][/] Session cookie: [bold]{cookie}[/]")
    return cookie
