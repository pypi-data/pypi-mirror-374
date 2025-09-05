import os

from sup.parser import Parser
from sup.vm import run as vm_run


def test_vm_imports_basic(tmp_path, monkeypatch):
    # Create a module file in a temp project and import it from VM
    (tmp_path / "mathlib.sup").write_text(
        (
            """
sup
  set pi to 3.14
  define function called square with x
    return multiply x and x
  end function
bye
"""
        ).strip(),
        encoding="utf-8",
    )

    code = (
        """
sup
  import mathlib
  print mathlib.pi
  print call mathlib.square with 3
bye
"""
    ).strip()

    # Ensure VM import resolver finds the module
    monkeypatch.chdir(tmp_path)
    program = Parser().parse(code)
    out = vm_run(program)
    assert out.splitlines() == ["3.14", "9.0"]


def test_vm_ask_reads_input(monkeypatch):
    # Mock input() to feed a deterministic value
    monkeypatch.setattr("builtins.input", lambda: "Alice")
    code = (
        """
sup
  ask for name
  print name
bye
"""
    ).strip()
    program = Parser().parse(code)
    out = vm_run(program)
    assert out.strip() == "Alice"


