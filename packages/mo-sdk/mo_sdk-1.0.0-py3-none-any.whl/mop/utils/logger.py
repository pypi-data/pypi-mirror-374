
import enum
import logging


class Colors(enum.Enum):
    GREY = "\033[90m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Colors.GREY.value,
        "INFO": Colors.BLUE.value,
        "WARNING": Colors.YELLOW.value,
        "ERROR": Colors.RED.value,
        "CRITICAL": Colors.MAGENTA.value,
    }

    RESET = Colors.RESET.value

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, "")
        record.levelname = f"{color}{levelname}{self.RESET}"
        return super().format(record)

def setup_logger(name="plugin-builder"):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Default log level, can be overridden by args
    return logger
