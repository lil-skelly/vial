from vial import logger, prompt
from vial.utils import encode, decode, werkzeug_remote_code_exec

def main():
    try:
        action = prompt.ask("[bold blue][?][/bold blue] What do you want to do?", choices=["encode", "decode", "rce"])
        if action == "encode":
            encode()
        if action == "decode":
            decode()
    except KeyboardInterrupt:
        logger.error("\nKeyboard Interrupt")
        exit(1)
        
if __name__ == "__main__":
    main()