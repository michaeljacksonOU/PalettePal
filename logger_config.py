import logging
import os
import sys

def setup_logger():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Running in development
        base_path = os.path.dirname(__file__)

    log_path = os.path.join(base_path, "palettepal.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.ERROR,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
