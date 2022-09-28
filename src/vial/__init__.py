from distutils.log import Log
from rich.console import Console
import rich.prompt
from vial.logger import Logger


# Declare constants
DEFAULT_SALT = "cookie-session"

console = Console()
prompt = rich.prompt.Prompt()
logger = Logger(console)
confirm = rich.prompt.Confirm()