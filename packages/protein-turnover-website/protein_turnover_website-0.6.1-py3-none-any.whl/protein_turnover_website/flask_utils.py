from __future__ import annotations

import gzip
import os
import tomllib
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Any

from flask import current_app
from flask import Flask
from flask import render_template
from flask import Response
from flask.config import Config
from flask_login import current_user
from jinja2 import FileSystemBytecodeCache
from jinja2 import FileSystemLoader
from jinja2 import TemplateNotFound
from markupsafe import Markup

from .utils import attrstr
from .utils import human
from .utils import signif

NAME = __name__.split(".", maxsplit=1)[0]


def error_resp(msg: str, code: int) -> Response:  # pragma: no cover
    return Response(msg, code, mimetype="text/plain")


def oktokill() -> bool:
    if current_user.is_authenticated:
        return True
    if current_app.config.get("WEBSITE_STATE", "multi_user") == "single_user":
        return True
    return current_app.config.get("CAN_KILL_JOBS", False)


def config_app(config: Config, from_file: bool = True) -> Config:
    config.from_object(f"{NAME}.config")
    config.from_object(f"{NAME}.non_user_config")
    if from_file:
        config.from_file("turnover-web.toml", load=tomllib.load, text=False, silent=True)  # type: ignore
    # we are running in embbed mode...
    # config.from_envvar("TURNOVER_SETTINGS", silent=True)
    if "TURNOVER_SETTINGS" in os.environ:
        config["SITE_PASSWORD"] = None
        config["CAN_KILL_JOBS"] = True
        config["ECHO_QUERY"] = False
        config["ADMINS"] = []
        # get rid of cloudflare challenge
        if "CF_IMAGE_FILENAME" in config:
            del config["CF_IMAGE_FILENAME"]
        config.from_file(os.environ["TURNOVER_SETTINGS"], load=tomllib.load, text=False)  # type: ignore

    return config


def register_bytecode_cache(app: Flask, directory: str = "bytecode_cache") -> None:
    cache = Path(directory)

    if not cache.is_absolute():
        cache = Path(app.instance_path).joinpath(directory)

    if not cache.is_dir():
        cache.mkdir(exist_ok=True, parents=True)
    app.jinja_options.update(
        {"bytecode_cache": FileSystemBytecodeCache(str(cache))},
    )


def try_init(module: str, app: Flask, url_prefix: str = "/") -> bool:
    import importlib

    try:
        mod = importlib.import_module(module)
        if not hasattr(mod, "init_app"):
            return False
        mod.init_app(app, url_prefix=url_prefix)
        app.logger.info("imported %s", module)
        return True
    except ImportError:  # pragma: no cover
        pass
    return False


def register_filters(app: Flask, base_template: str = "raw.html") -> None:
    """Register page not found filters cdn_js, cdn_css methods."""

    with app.open_resource("cdn.toml", mode="rb") as fp:
        CDN = tomllib.load(fp)  # type: ignore

    def include_raw(filename: str) -> Markup:
        def markup(loader: FileSystemLoader | None) -> Markup | None:
            if loader is None:  # pragma: no cover
                return None
            for path in loader.searchpath:
                f = Path(path).joinpath(filename)
                if f.is_file():
                    with gzip.open(f, "rt", encoding="utf8") as fp:
                        return Markup(fp.read())
            return None

        if filename.endswith((".gz", ".svgz")):
            for loader in chain(
                [app.jinja_loader],
                (bp.jinja_loader for bp in app.blueprints.values()),
            ):
                if isinstance(loader, FileSystemLoader):
                    ret = markup(loader)
                    if ret is not None:
                        return ret
            raise TemplateNotFound(filename)
        loader = app.jinja_env.loader
        if loader is None:  # pragma: no cover
            return Markup("")
        src = loader.get_source(app.jinja_env, filename)[0]
        return Markup(src)

    def include_css(filename: str) -> Markup:
        # to avoid formatting problems with <style>{% include "file.css" %}</style>
        loader = app.jinja_env.loader
        if loader is None:  # pragma: no cover
            return Markup("")
        src = loader.get_source(app.jinja_env, filename)[0]

        return Markup(f"<style>{src}</style>")

    def cdn_js(key: str, **kwargs: Any) -> Markup:
        js = CDN[key]["js"]
        async_ = "async" if js.get("async", False) else ""
        attrs = attrstr(kwargs)
        integrity = js.get("integrity")
        integrity = f'integrity="{integrity}"' if integrity else ""

        return Markup(
            f"""<script src="{js['src']}" {async_}
            {integrity} {attrs}crossorigin="anonymous"></script>""",
        )

    def cdn_css(key: str, **kwargs: Any) -> Markup:
        css = CDN[key]["css"]
        attrs = attrstr(kwargs)
        integrity = css.get("integrity")
        integrity = f'integrity="{integrity}"' if integrity else ""
        return Markup(
            f"""<link rel="stylesheet" href="{css['href']}"
            {integrity} {attrs}crossorigin="anonymous">""",
        )

    # for nunjucks includes
    app.jinja_env.globals["include_raw"] = include_raw
    app.jinja_env.globals["include_css"] = include_css
    app.jinja_env.globals["cdn_js"] = cdn_js
    app.jinja_env.globals["cdn_css"] = cdn_css
    app.jinja_env.globals["base_template"] = base_template
    app.jinja_env.globals["year"] = datetime.now().year

    app.template_filter("human")(human)
    app.template_filter("signif")(signif)

    @app.template_filter()
    def split(
        s: str,
        sep: str | None = None,
    ) -> list[str]:  # pragma: no cover
        return [] if not s else (s.split(sep) if sep is not None else s.split())

    @app.errorhandler(404)
    def page_not_found(
        e: Exception,
    ) -> tuple[str, int]:
        return render_template("errors/404.html"), 404
