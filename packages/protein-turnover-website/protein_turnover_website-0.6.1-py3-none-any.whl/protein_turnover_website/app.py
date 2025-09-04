from __future__ import annotations

import logging
import os
from typing import Any

import matplotlib
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .flask_utils import config_app
from .flask_utils import NAME
from .flask_utils import register_bytecode_cache
from .flask_utils import register_filters
from .flask_utils import try_init
from .logger import init_email_logger
from .utils import git_version
from .utils import pipy_version


def create_init_app(from_file: bool = True) -> Flask:
    app = Flask(
        NAME,
        instance_relative_config=True,
        template_folder="templates",
    )
    config_app(app.config, from_file)
    if "TURNOVER_SETTINGS" in os.environ:
        app.config["FIXSQLITE"] = False
    version = git_version()
    if version is None:
        version = pipy_version()
    else:
        version = version[:7]

    version = version or "unknown"
    app.config["GIT_VERSION"] = version
    if app.debug:  # pragma: no cover
        # avoid caching ...
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    if app.config.get("PROXY_FIX", False):
        app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore[assignment]
    if app.config.get("WEBSITE_STATE", "multi_user") != "multi_user":
        app.logger.setLevel(logging.INFO)
    return app


def create_app(cfg: dict[str, Any] | None = None) -> Flask:
    app = create_init_app(cfg is None)
    if cfg is not None:
        app.config.update(cfg)
    init_full_app(app)
    return app


def create_view_app(cfg: dict[str, Any] | None = None) -> Flask:
    app = create_init_app(cfg is None)
    if cfg is not None:
        app.config.update(cfg)
    init_view_app(app)
    return app


def init_full_app(app: Flask) -> None:
    init_email_logger(app)  # email logger requires config.ADMINS = [email]

    # non-interactive backends: agg, cairo, pdf, pgf, ps, svg, template

    matplotlib.use(app.config["MATPLOTLIB_BACKEND"], force=True)

    from .inspect_view import init_app as init_inspect

    init_inspect(app)

    from .index_view import init_app as init_index

    init_index(app)

    from .jobs_view import init_app as init_jobs

    init_jobs(app)

    from .login.login_view import init_app as init_login_app

    init_login_app(app)

    from .explorer.explorer_view import init_app as init_explorer

    init_explorer(app)

    register_filters(app)

    register_bytecode_cache(app)

    try_init("cloudflare_challenge", app, url_prefix="/")

    from .commands import turover_cli

    app.cli.add_command(turover_cli)


def init_view_app(app: Flask) -> None:
    """Just single page view of results"""

    # non-interactive backends: agg, cairo, pdf, pgf, ps, svg, template

    matplotlib.use(app.config["MATPLOTLIB_BACKEND"], force=True)

    from .inspect_view import init_view

    dataid = app.config["DATAID"]

    init_view(app, dataid)

    register_filters(app, base_template="view.html")

    register_bytecode_cache(app)
