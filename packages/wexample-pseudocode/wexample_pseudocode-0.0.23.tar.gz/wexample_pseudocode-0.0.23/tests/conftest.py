from __future__ import annotations

from pathlib import Path

import pytest
from wexample_pseudocode.generator.pseudocode_generator import PseudocodeGenerator


@pytest.fixture()
def resources_dir() -> Path:
    # Mirror PHP test resources structure under python package tests
    return Path(__file__).parent / "resources" / "item" / "constant"


@pytest.fixture()
def generator() -> PseudocodeGenerator:
    return PseudocodeGenerator()
