from pathlib import Path
import json as pyjson
from src.api import config


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
