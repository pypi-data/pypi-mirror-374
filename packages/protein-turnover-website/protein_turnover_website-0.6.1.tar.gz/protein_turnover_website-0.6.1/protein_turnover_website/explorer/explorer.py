from __future__ import annotations

import logging
import os
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from os import stat_result
from pathlib import Path
from typing import Literal
from typing import TypeAlias
from typing import TypedDict

from flask import current_app
from flask import Flask
from flask import request
from markupsafe import Markup

from ..utils import LogRecord

logger = logging.getLogger("explorer")


class FileDisplayJSON(TypedDict):
    name: str
    mtime: float
    size: int
    is_dir: bool
    icon: str


class FileDisplay:
    def __init__(self, file: Path):
        self.file = file
        self.stat: stat_result | None = None

    @property
    def icon(self) -> str:
        return (
            '<i class="far fa-folder"></i>'
            if self.file.is_dir()
            else '<i class="far fa-file"></i>'
        )

    @property
    def is_dir(self) -> bool:
        return self.file.is_dir()

    @property
    def name(self) -> str:
        return self.file.name

    @property
    def mtime(self) -> datetime:
        if self.stat is None:
            self.stat = self.file.stat()
        return datetime.fromtimestamp(self.stat.st_mtime)

    @property
    def size(self) -> int:
        if self.stat is None:
            self.stat = self.file.stat()
        return self.stat.st_size

    def tojson(self) -> FileDisplayJSON:
        return FileDisplayJSON(
            name=self.name,
            mtime=self.mtime.timestamp(),
            size=self.size,
            is_dir=self.is_dir,
            icon=self.icon,
        )


class DotDot(FileDisplay):
    @property
    def name(self) -> str:
        return ".."

    @property
    def icon(self) -> str:
        return '<i class="fas fa-level-up-alt"></i>'


Sorton: TypeAlias = Literal["time", "size", "name", "type"]

KEYS = {
    "time": lambda f: f.mtime,
    "size": lambda f: f.size,
    "name": lambda f: f.name,
    "type": lambda f: ("a" if f.is_dir else "b") + f.name,
}


class State(TypedDict):
    parent: str
    mountpoint: str
    sorton: Sorton
    ascending: bool


class BreadCrumbJSON(State):
    name: str


@dataclass
class BreadCrumb:
    mountpoint: MountPoint
    path: Path
    name: str
    sorton: Sorton
    ascending: bool

    @property
    def state(self) -> State:
        return State(
            parent=str(self.path),
            mountpoint=self.mountpoint.label,
            sorton=self.sorton,
            ascending=self.ascending,
        )

    # def tojson(self) -> BreadCrumbJSON:
    #     d: BreadCrumbJSON = self.state  # type: ignore
    #     d["name"] = self.name
    #     return d


class ExplorerJSON(State):
    directory_listing: list[FileDisplayJSON]
    breadcrumbs: list[BreadCrumbJSON]


@dataclass
class Explorer:
    mountpoint: str
    parent: Path
    directory_listing: list[FileDisplay]
    breadcrumbs: list[BreadCrumb]
    sorton: Sorton
    ascending: bool

    def sorted(self, sorton: str) -> Markup:
        if self.sorton != sorton:
            return Markup(' <i class="fas fa-sort-down" style="opacity:.2"></i>')
        d = "down" if self.ascending else "up"
        return Markup(f' <i class="fas fa-sort-{d}"></i>')

    @property
    def state(self) -> State:
        return State(
            parent=str(self.parent),
            mountpoint=self.mountpoint,
            sorton=self.sorton,
            ascending=self.ascending,
        )

    def directory(self, mountpoints: MountPoints) -> Path | None:
        m = mountpoints.get(self.mountpoint)
        if m is None:  # pragma: no cover
            return None
        return m.mountpoint.joinpath(self.parent)

    # def tojson(self) -> dict[str, Any]:
    #     ret: dict = self.state  # type: ignore
    #     ret["directory_listing"] = [d.tojson() for d in self.directory_listing]
    #     ret["breadcrumbs"] = [d.tojson() for d in self.breadcrumbs]
    #     return ret


class MountPoint:
    HIDDEN = (".",)
    """If True then soft links will be OK"""

    def __init__(
        self,
        mountpoint: str,
        label: str | None = None,
        glob: str | None = None,
        *,
        exists: bool = True,
        allow_links: bool = False,
    ):
        self.allow_links = allow_links
        self.mountpoint = Path(mountpoint).expanduser()
        if not self.allow_links:
            self.mountpoint = self.mountpoint.resolve()
        else:
            self.mountpoint = self.mountpoint.absolute()
        if not self.mountpoint.exists():
            if exists:
                # logger.error("mountpoint doesn't exist: %s", self.mountpoint)
                raise ValueError(f"mountpoint doesn't exist {mountpoint}")

        if label is None:
            label = self.mountpoint.name.title()
        self.label = label
        self.glob = re.compile(glob, re.I) if glob else None

    def home(self) -> Explorer | None:
        return self.change_directory("")

    def change_directory(
        self,
        parent: str,
        name: str | None = None,
        sorton: Sorton = "name",
        ascending: str = "true",
    ) -> Explorer | None:
        mountpoint = self.mountpoint
        if ".." in parent:
            logger.warning("parent has .. %s for %s", parent, self.mountpoint)
            return None
        root = mountpoint.joinpath(*parent.split(os.path.sep))
        if not self.allow_links:
            root = root.resolve()

        if name is None:
            pass
        elif name != "..":
            root = root.joinpath(name)
        else:
            root = root.parent
        if not root.is_relative_to(mountpoint):  # pragma: no cover
            logger.warning(
                'new root "%s" is not relative to mountpoint "%s"',
                root,
                mountpoint,
            )
            return None
        up: list[FileDisplay] = [DotDot(root.parent)] if root != mountpoint else []

        def match(f: Path) -> bool:
            if self.glob is None:
                return True
            if self.glob.match(f.name):
                return True
            return False

        directory_listing = up + sorted(
            (
                FileDisplay(f)
                for f in root.iterdir()
                if f.exists()
                and not f.name.startswith(self.HIDDEN)
                and (match(f) or f.is_dir())
            ),
            key=KEYS[sorton],
            reverse=ascending != "true",
        )
        return Explorer(
            self.label,
            parent=root.relative_to(mountpoint),
            directory_listing=directory_listing,
            breadcrumbs=self.breadcrumbs(root, sorton, ascending == "true"),
            sorton=sorton,
            ascending=ascending == "true",
        )

    def breadcrumbs(
        self,
        root: Path,
        sorton: Sorton,
        ascending: bool,
    ) -> list[BreadCrumb]:
        rroot = root.relative_to(self.mountpoint)
        if root == self.mountpoint:
            return [BreadCrumb(self, rroot, self.label, sorton, ascending)]
        return [
            *[
                BreadCrumb(self, p, p.name if p.name else self.label, sorton, ascending)
                for p in reversed(rroot.parents)
            ],
            BreadCrumb(self, rroot, root.name, sorton, ascending),
        ]


def find_directory_from_request(mountpoints: MountPoints) -> Explorer | None:
    # mountpoint, parent, sorton, ascending
    v = dict(request.values)

    mountpoint = v.pop("mountpoint", None)
    if not mountpoint:  # pragma: no cover
        return None
    mount = mountpoints.get(mountpoint)
    if mount is None:  # pragma: no cover
        return None
    parent = v.pop("parent", ".")
    if ".." in parent:  # pragma: no cover
        return None
    v = {k: v for k, v in v.items() if k in {"name", "sorton", "ascending"}}
    return mount.change_directory(parent, **v)  # type: ignore


def find_mountpoint_for(
    path: Path,
    mountpoints: MountPoints,
) -> MountPoint | None:
    for m in mountpoints.mountpoints:
        if path.is_relative_to(m.mountpoint):  # type: ignore
            return m
    return None  # pragma: no cover


def safe_repr(
    path: Path,
    mountpoints: MountPoints,
) -> tuple[MountPoint, Path, bool]:
    m = find_mountpoint_for(path, mountpoints)
    if m is None:
        return (
            MountPoint(str(path.parent), "unknown", exists=False),
            Path(path.name),
            False,
        )
    return m, path.relative_to(m.mountpoint), True


# def safe_repr_for(
#     path: Path,
# ) -> tuple[MountPoint, Path, bool]:
#     mountpoints = get_mountpoints()
#     return safe_repr(path, mountpoints)


class MountPoints:
    def __init__(
        self,
        mountpoints: list[MountPoint],
        extra: list[MountPoint] | None = None,  # mountpoints like cachedir etc
    ):
        if extra is None:
            extra = []
        self.mountpoints = mountpoints
        self._mp = {m.label: m for m in mountpoints}

        def pat(m: MountPoint) -> str:
            return f"(?P<{re.escape(m.label)}>{re.escape(str(m.mountpoint))})"

        self.pattern = re.compile(
            "|".join(pat(m) for m in chain(mountpoints, extra)),
        )

    def get(self, label: str) -> MountPoint | None:
        return self._mp.get(label)

    def sanitize_log(self, results: list[LogRecord]) -> list[LogRecord]:
        """remove any full pathnames from logfile for viewing on web"""

        def repl(m: re.Match) -> str:
            for label, matched in m.groupdict().items():
                if matched:
                    return f"{label}:"
            return "unknown:"  # pragma: no cover

        ret = []
        for r in results:
            msg, cnt = self.pattern.subn(repl, r.msg)
            if cnt:
                r = r._replace(msg=msg)
            ret.append(r)
        return ret


def find_explorer(mountpoints: MountPoints) -> Explorer | None:
    mp = request.values.get("mountpoint", "HOME")
    path = request.values.get("path", None)

    mount = mountpoints.get(mp)
    if mount is None:
        mount = mountpoints.mountpoints[0]

    if path is not None:
        explorer = mount.change_directory(path)
        if explorer is None:
            explorer = mount.home()
    else:
        explorer = mount.home()

    return explorer


def get_mountpoints() -> MountPoints:
    mountpoints: MountPoints = current_app.extensions["MOUNTPOINTS"]
    return mountpoints


def init_mountpoints(app: Flask) -> None:
    from ..jobs import get_jobsdir_list

    ALLOW_LINKS = app.config.get("ALLOW_LINKS", False)
    mm = app.config.get("MOUNTPOINTS")

    # NOTE: may come from a .toml file so will be
    # a list of lists
    def okargs(m):
        return isinstance(m, str) or (isinstance(m, Sequence) and len(m) in {1, 2, 3})

    if not isinstance(mm, Sequence) or len(mm) == 0 or not all(okargs(m) for m in mm):
        raise ValueError(
            "config.MOUNTPOINTS should be a list of str/tuples/list",
        )

    mm = [[s] if isinstance(s, str) else s for s in mm]

    mountpoints = [MountPoint(*m, allow_links=ALLOW_LINKS) for m in mm]

    if not sorted({m.label for m in mountpoints}) == sorted(
        m.label for m in mountpoints
    ):
        raise ValueError(
            "config.MOUNTPOINTS should have different labels for different mountpoints",
        )
    jobsdir_list = get_jobsdir_list(app)

    cachedir = app.config.get("CACHEDIR")
    # if cachedir is None:
    #     raise RuntimeError("please specify config.CACHEDIR directory")
    # sanitize jobs directory too...

    # extras are just for sanitizing log files
    extra = [MountPoint(str(jobsdir_list[0]), "jobs", exists=False)]
    if cachedir is not None:
        extra.append(MountPoint(str(cachedir), "cachedir", exists=False))
    app.extensions["MOUNTPOINTS"] = MountPoints(mountpoints, extra=extra)
