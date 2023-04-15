from vial import prompt, web_session
import vial


def authenticate(
    parameters: dict,
    url: str = "http://localhost:5000/",
) -> None:
    """
    Authenticate to the debug console
    :param url: url to authenticate to
    """
    while True:
        pin = prompt.ask("[bold blue][?][/] Enter pin", password=True)
        parameters["pin"] = pin

        resp = web_session.post(url, params=parameters).json()
        vial.log.info(resp)

        if not resp["auth"]:
            vial.log.error(f"Failed to authenticate with pin {pin}.")
            continue

        vial.log.info(f"Authenticated with pin {pin}")
        break
