from rich.logging import RichHandler
import logging

class Logger:
    """
    Custom logger class for rich logging
    """
    def __init__(self, console) -> None:
        logging.basicConfig(
            format="%(message)s",
            datefmt="[%X]",
            level=logging.INFO,
            handlers=[RichHandler(console=console, markup=True)]
        )

        RichHandler.KEYWORDS = ["[?]", "[✗]", "[⚠]", "[✓]"]
        self.log: object = logging.getLogger("rich")

    def logger(
        self,
        exception_: str,
        message: str
    ) -> None:
        """
        Logs a message to the console with its corresponding exception

        :param exception_: Exception type
        :param message: Message to log
        :return: None
        """
        match exception_:
            case "info":
                self.log.info(f"[?] {message}")      
            case "error":
                self.log.error(f"[✗]{message}")
            case "warning":
                self.log.warning(f"[⚠] {message}")
            case "success":
                self.log.info(f"[✓] {message}")

