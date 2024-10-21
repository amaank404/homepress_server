import secrets

from .config import config


def create_safe_name():
    while True:
        t = secrets.token_hex(32)
        if not (config.uploads_directory / t).exists():
            return t