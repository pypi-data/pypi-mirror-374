from __future__ import annotations

from pathlib import Path

import yaml
from wexample_pseudocode.generator.code_generator import CodeGenerator
from wexample_pseudocode.generator.pseudocode_generator import PseudocodeGenerator


def _res_dir(name: str) -> Path:
    return Path(__file__).parent / "resources" / "item" / "function"


def test_function_basic_py_to_yaml() -> None:
    d = _res_dir("function")
    py = (d / "basic_function.py").read_text(encoding="utf-8")
    expected = yaml.safe_load((d / "basic_function.yml").read_text(encoding="utf-8"))

    actual = PseudocodeGenerator().generate_config_data(py)
    assert actual == expected


def test_function_basic_yaml_to_py() -> None:
    d = _res_dir("function")
    yml = (d / "basic_function.yml").read_text(encoding="utf-8")
    expected_code = (d / "basic_function.py").read_text(encoding="utf-8").strip()

    code = CodeGenerator().generate(yml)
    assert code.strip() == expected_code


def test_function_complex_py_to_yaml() -> None:
    d = _res_dir("function")
    py = (d / "complex_function.py").read_text(encoding="utf-8")
    expected = yaml.safe_load((d / "complex_function.yml").read_text(encoding="utf-8"))

    actual = PseudocodeGenerator().generate_config_data(py)
    assert actual == expected


def test_function_complex_yaml_to_py() -> None:
    d = _res_dir("function")
    yml = (d / "complex_function.yml").read_text(encoding="utf-8")
    expected_code = (d / "complex_function.py").read_text(encoding="utf-8").strip()

    code = CodeGenerator().generate(yml)
    assert code.strip() == expected_code
