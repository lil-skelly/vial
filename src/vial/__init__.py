import logging
from rich.logging import RichHandler
from rich.prompt import Prompt as prompt
from rich.prompt import Confirm as confirm
import requests

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

log = logging.getLogger("rich")

# Declare constants
DEFAULT_SALT = "cookie-session"
DEFAULT_COOKIE_NAME = "session"
DEFAULT_USER_AGENT = "Vial/1.0"

FETCHED_COOKIE = None

web_session = requests.Session()
