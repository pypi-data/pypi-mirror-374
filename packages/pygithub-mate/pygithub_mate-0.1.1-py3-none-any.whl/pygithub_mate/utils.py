# -*- coding: utf-8 -*-

from pathlib import Path

from .vendor.hashes import hashes

hashes.use_sha256()


def calculate_sha256(path: Path) -> str:
    return hashes.of_file(str(path))
