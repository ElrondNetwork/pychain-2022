from pathlib import Path


def read_text(path: Path):
    with open(path, "r") as text_file:
        return text_file.read()
