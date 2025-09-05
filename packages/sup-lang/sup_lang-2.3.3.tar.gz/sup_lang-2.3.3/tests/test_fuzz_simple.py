import io
import contextlib

from hypothesis import given, strategies as st

from sup.cli import run_source


def run_transpiled(code: str) -> str:
    py = run_source(code, emit="python")
    buf = io.StringIO()
    ns: dict = {"__name__": "__main__"}
    with contextlib.redirect_stdout(buf):
        exec(py, ns)
    return buf.getvalue()


@given(st.lists(st.integers(min_value=0, max_value=9), min_size=1, max_size=6))
def test_fuzz_sum_of_small_ints_agrees_with_transpiled(nums: list[int]):
    # Build a small SUP program that sums provided integers
    body_lines = ["set total to 0"]
    for n in nums:
        body_lines.append(f"set total to add total and {n}")
    body_lines.append("print total")
    code = ("\n".join(["sup"] + ["  " + ln for ln in body_lines] + ["bye"]))

    out_interp = run_source(code)
    out_transp = run_transpiled(code)
    assert out_interp == out_transp


