import logging



class CreateLogger:
    def __init__(self) -> None:
        self.info("Start JooYT Program")
        self.info("="*50)
        self.debug("Harmless debug Message")
        self.info("Just an information")
        self.warning("Its a Warning")
        self.error("Did you try to divide by zero")
        self.critical("Internet is down")
CreateLogger()