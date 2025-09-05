from __future__ import annotations

import time
from pathlib import Path

import statistics as stats

from sup.cli import run_source


CASES: list[tuple[str, str]] = [
    (
        "arith_loop",
        (
            "sup\n"
            "set total to 0\n"
            "repeat 10000 times\n"
            "set total to add total and 3\n"
            "endrepeat\n"
            "print the result\n"
            "bye\n"
        ),
    ),
    (
        "json_io",
        (
            "sup\n"
            "set s to json stringify of make map\n"
            "print s\n"
            "bye\n"
        ),
    ),
]


def run_case(name: str, code: str, warmup: int = 2, iters: int = 5) -> dict[str, float]:
    for _ in range(warmup):
        run_source(code)
    times: list[float] = []
    for _ in range(iters):
        t0 = time.perf_counter()
        run_source(code)
        times.append(time.perf_counter() - t0)
    return {
        "min": min(times),
        "median": stats.median(times),
        "mean": stats.mean(times),
        "max": max(times),
    }


def main() -> None:
    results: dict[str, dict[str, float]] = {}
    for name, code in CASES:
        results[name] = run_case(name, code)
    # Print simple table
    print("name,min,median,mean,max")
    for name, m in results.items():
        print(f"{name},{m['min']:.6f},{m['median']:.6f},{m['mean']:.6f},{m['max']:.6f}")


if __name__ == "__main__":
    main()


