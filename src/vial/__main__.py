import vial
from vial.utils import Proxy, fetch_cookie
import argparse
import requests
from rich.prompt import Prompt

parser = argparse.ArgumentParser(
    description="Vial - A blazing fast python framework focused on exploiting Werkzeug based applications."
)

parser.add_argument(
    "--server", "-s", help="Web server to automatically fetch the vial.session from"
)
parser.add_argument(
    "--cookie-name",
    "-cN",
    default=vial.DEFAULT_COOKIE_NAME,
    help=(
        "Cookie to look for when automatically fetching the vial.session from a web application.\n"
        + f"Werkzeug uses '{vial.DEFAULT_COOKIE_NAME}' by default.\n"
        + "Only use when --server is set."
    ),
)
parser.add_argument(
    "--proxy",
    "-p",
    help=("HTTP(S) proxy to use for requests.\n" + "Only use when --from is set."),
)
parser.add_argument(
    "--insecure",
    "-i",
    action="store_true",
    help=(
        "Disable SSL certificate verification.\n"
        + "Useful when the server is using a self-signed certificate."
    ),
)
parser.add_argument(
    "--user-agent",
    "-uA",
    default=vial.DEFAULT_USER_AGENT,
    help=(
        "User-Agent to use when making requests to web application.\n"
        + f"Defaults to {vial.DEFAULT_USER_AGENT}.\n"
    ),
)
parser.add_argument(
    "--config",
    "-c",
    type=str,
    help=(
        "TOML configuration file to use."
    ),
)

args = parser.parse_args()


def main() -> None:
    try:
        if args.config:
            vial.CONFIG = args.config
        if args.proxy and isinstance(args.proxy, str):
            vial.web_session.proxies: Proxy = {"http": args.proxy, "https": args.proxy}
            vial.log.info(f"Using proxy: {args.proxy}")

        if (
            args.user_agent
            and args.user_agent != vial.DEFAULT_USER_AGENT
            and isinstance(args.user_agent, str)
        ):
            vial.session.user_agent = args.user_agent
            vial.log.info(f"Using User-Agent: {vial.session.user_agent}")

        if args.server:
            vial.session.verify = not args.insecure

            if args.insecure:
                from requests.packages.urllib3.exceptions import InsecureRequestWarning

                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

            vial.FETCHED_COOKIE = fetch_cookie(
                host=args.server,
                cookie_name=args.cookie_name,
                session=vial.web_session,
            )

        # TODO: User actions
        action = Prompt.ask(
            "[bold blue][?][/] Select an action", choices=["encode", "decode", "pin"]
        )
        if vial.FETCHED_COOKIE:
            vial.log.info(
                f"Using pre-fetched cookie: [bold]{vial.FETCHED_COOKIE}[/] ({args.server})"
            )

        match action:
            case "decode":
                from vial.utils import decode_handler

                decode_handler()
            case "encode":
                from vial.utils import encode_handler

                encode_handler()
            case "pin":
                if not args.config:
                    vial.log.error(
                        "[underline]pin[/] mode can only be used along the [bold]--config[/] argument."
                    )
                else:
                    from vial.utils import generate_pin
                    generate_pin(vial.CONFIG)
    except KeyboardInterrupt:
        vial.log.error("Received [bold]keyboard interrupt[/]")


if __name__ == "__main__":
    main()
