from __future__ import annotations

import math
import subprocess
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from shutil import which
from typing import Any
from typing import Callable
from typing import cast
from typing import Hashable
from typing import Iterator
from typing import NamedTuple

import pandas as pd
from markupsafe import escape


def git_version() -> str | None:
    git = which("git")
    if git is None:  # pragma: no cover
        return None
    cwd = Path(__file__).parent
    r = subprocess.run(
        [git, "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        check=False,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
    )
    if r.returncode or not r.stdout:  # pragma: no cover
        return None
    return r.stdout.decode("ascii").strip()


def pipy_version() -> str | None:
    try:
        from importlib.metadata import version

        return f"website: {version('protein_turnover_website')}, backend: {version('protein_turnover')}"
    except Exception:  # pragma: no cover
        return None


def attrstr(kwargs: dict[str, Any]) -> str:
    attrs = " ".join(
        f'{escape(k.replace("_", "-"))}="{escape(v)}"'
        for k, v in kwargs.items()
        if v is not None
    )
    if attrs:
        attrs += " "
    return attrs


def human(num: int, suffix: str = "B", scale: int = 1) -> str:
    if not num:
        return f"0{suffix}"
    num *= scale
    magnitude = int(math.floor(math.log(abs(num), 1000)))
    val = num / math.pow(1000, magnitude)
    if magnitude > 7:  # pragma: no cover
        return f"{val:.1f}Y{suffix}"
    e = ["", "k", "M", "G", "T", "P", "E", "Z"][magnitude]
    if not e:
        return f"{int(num)}{suffix}"
    return f"{val:3.1f}{e}{suffix}"


def rmfiles(files: list[str]) -> None:
    for f in files:
        try:
            Path(f).unlink(missing_ok=True)
        except OSError:
            pass


class LogRecord(NamedTuple):
    time: datetime
    level: str
    worker: int
    msg: str


def read_log_lines(
    logfile: Path,
    start: int = 0,
    encoding: str = "utf-8",
) -> Iterator[str]:
    import os

    with logfile.open("rb") as f:
        if start != 0:
            st = logfile.stat()
            if start > 0:
                start = min(start, st.st_size)
                f.seek(start)
            else:
                start = max(start, -st.st_size)
                f.seek(start, os.SEEK_END)
            for c in iter(lambda: f.read(1), b""):
                if c == b"\n":
                    break
        with TextIOWrapper(f, encoding=encoding) as fp:
            for line in fp:
                line = line[:-1]
                yield line


def read_log(
    logfile: Path,
    start: int = 0,
    encoding: str = "utf-8",
) -> Iterator[LogRecord]:
    try:
        for line in read_log_lines(logfile, start, encoding):
            level, time, worker, msg = line.split("|", maxsplit=3)
            time = time[1:-1]
            dttime = datetime.strptime(time, "%Y-%m-%d %H:%M:%S,%f")
            yield LogRecord(dttime, level.strip(), int(worker), msg.strip())
    except ValueError:  # pragma: no cover
        pass


def signif(x: float | int, digits: int = 6) -> float | int:
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)


def round_df(
    df: pd.DataFrame,
    digits: int = 5,
) -> Callable[[dict[Hashable, Any]], dict[str, Any]]:
    floatcols: list[str] = [col for col in df.columns if df[col].dtype.kind == "f"]

    def roundfloat(d: dict[Hashable, Any]) -> dict[str, Any]:
        for k in floatcols:
            d[k] = signif(d[k], digits=digits)
        return cast(dict[str, Any], d)

    return roundfloat
