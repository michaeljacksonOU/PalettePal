import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "palettepal.log"

def setup_logger():
  logging.basicConfig(
    filename=LOG_PATH,
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s"
  )
