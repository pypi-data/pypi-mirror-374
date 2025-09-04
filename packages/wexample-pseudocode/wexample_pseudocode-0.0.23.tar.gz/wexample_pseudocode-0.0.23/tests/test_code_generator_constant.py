from __future__ import annotations

from wexample_pseudocode.generator.code_generator import CodeGenerator


def test_code_generator_constant(resources_dir) -> None:
    yml_path = resources_dir / "constant_using_const.yml"
    expected_code_path = resources_dir / "constant_using_const.py"

    gen = CodeGenerator()
    output = gen.generate(yml_path.read_text(encoding="utf-8"))

    # Normalize trailing newline for comparison simplicity
    assert output.strip() == expected_code_path.read_text(encoding="utf-8").strip()
