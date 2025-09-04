from __future__ import annotations

from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import render_template
from flask import Response
from flask import url_for


view = Blueprint("view", __name__)


@view.route("/")
def index() -> Response:
    return current_app.redirect(url_for("job.index"), 302)  # type: ignore
    # return render_template("index.html")


@view.route("/configuration.html")
def configuration() -> str:
    return render_template("configuration.html")


def init_app(app: Flask, url_prefix: str = "/") -> None:
    app.register_blueprint(view, url_prefix=url_prefix)
