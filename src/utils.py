import json
import logging
from pathlib import Path
import string

from pdfminer.high_level import extract_text

log = logging.getLogger(__name__)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def strip_punctuation_lower(s: str):
    """Remove punctuation and spaces from a string and make all characters lower case"""
    return s.translate(str.maketrans("", "", string.punctuation)).lower().replace(" ",  "")


def extract_data_from_file(input_file_path: str) -> str:
    suffix = Path(input_file_path).suffix

    if suffix == ".txt":
        with open(input_file_path, "r") as f:
            text = f.read()
    elif suffix == ".pdf":
        text = extract_text(input_file_path)
    else:
        raise Exception("Invalid file type supplied. Must be one of ['.txt', '.pdf']")

    log.info(f"Read data from {input_file_path}")
    return text
