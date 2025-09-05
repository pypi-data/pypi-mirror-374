import io
import contextlib

from sup.cli import run_source


def run_transpiled(code: str) -> str:
    py = run_source(code, emit="python")
    buf = io.StringIO()
    ns: dict = {"__name__": "__main__"}
    with contextlib.redirect_stdout(buf):
        exec(py, ns)
    return buf.getvalue()


def test_conformance_arithmetic_and_print():
    code = (
        """
sup
  set x to add 2 and 3
  print x
  print the result
bye
"""
    ).strip()
    out_interp = run_source(code)
    out_transp = run_transpiled(code)
    assert out_interp == out_transp


def test_conformance_functions_and_calls():
    code = (
        """
sup
  define function called addtwo with a and b
    return add a and b
  end function
  print call addtwo with 4 and 5
bye
"""
    ).strip()
    out_interp = run_source(code)
    out_transp = run_transpiled(code)
    assert out_interp == out_transp


def test_conformance_control_flow_and_repeat():
    code = (
        """
sup
  set x to 0
  repeat 3 times
    set x to add x and 2
  endrepeat
  if x is greater than 5 then
    print x
  else
    print "no"
  end if
bye
"""
    ).strip()
    out_interp = run_source(code)
    out_transp = run_transpiled(code)
    assert out_interp == out_transp


