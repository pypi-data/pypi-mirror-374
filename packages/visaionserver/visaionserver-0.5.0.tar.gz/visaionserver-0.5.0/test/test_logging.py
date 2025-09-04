from visaionserver.core import LOGGER

if __name__ == "__main__":
    LOGGER.info("This is an info message")
    LOGGER.error("This is an error message")
    LOGGER.warning("This is a warning message")
    LOGGER.debug("This is a debug message")
    LOGGER.critical("This is a critical message")
    LOGGER.exception("This is an exception message")