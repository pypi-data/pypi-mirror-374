from __future__ import annotations

from typing import cast

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import Response
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import LoginManager
from flask_login import logout_user
from flask_login import UserMixin


login_manager = LoginManager()
login_manager.login_view = "login.login_cmd"  # type: ignore


def get_login_db() -> str | dict[str, str] | None:
    return current_app.config.get("SITE_PASSWORD", None)


def get_user_password(email: str) -> str | None:
    ret = get_login_db()
    if ret is None:
        return None
    if isinstance(ret, str):
        return ret
    if email in ret:
        return ret[email]
    return None


class User(UserMixin):
    def __init__(self, email: str):
        self.email = email

    def get_id(self) -> str:
        return self.email


@login_manager.user_loader
def load_user(email: str) -> User | None:
    pwd = get_user_password(email)
    if not pwd:  # pragma: no cover
        return None
    return User(email)


def okemail(email: str) -> bool:
    if "@" not in email:
        return False

    valid = get_login_db()
    if valid is None:  # pragma: no cover
        return False
    if isinstance(valid, str):  # pragma: no cover
        return True

    return email.lower() in valid


login = Blueprint("login", __name__, template_folder="templates")


@login.route("/login", methods=["POST", "GET"])
def login_cmd() -> str | Response:
    email = ""
    email_required = isinstance(get_login_db(), dict)

    def render(
        badpwd: bool = False,
        bademail: bool = False,
    ) -> str:
        return render_template(
            "login.html",
            badpwd=badpwd,
            email=email or "",
            bademail=bademail,
            email_required=email_required,
        )

    if request.method in ["GET", "HEAD"]:
        return render()

    if not request.method == "POST":
        abort(404)

    pwd = request.values.get("password")
    email = request.values.get("email", "")

    def bademail() -> str:
        return render(bademail=True)

    if email_required:
        if not email:
            return bademail()

        if not okemail(email):
            return bademail()

    if not pwd or pwd != get_user_password(email):
        return render(badpwd=True)

    # use REMEMBER_COOKIE_DURATION seconds or timedelta
    email = email or current_app.config.get(
        "MAIL_PLACEHOLDER",
        "global.you@turnover.org",
    )
    login_user(User(email), remember=False)

    nexturl = request.values.get("next")
    if nexturl and nexturl.startswith("/"):
        return cast(Response, redirect(nexturl))

    return cast(Response, redirect("/"))


@login.route("/logout")
def logout_cmd() -> Response:
    logout_user()
    return cast(Response, redirect(url_for("login.login_cmd")))


def init_app(app: Flask, url_prefix: str = "/") -> None:
    login_manager.init_app(app)  # ensure current_user is available in templates

    db = app.config.get("SITE_PASSWORD")
    if db is None:
        # no password... don't register a login form
        return
    if not isinstance(db, (str, dict)):  # pragma: no cover
        app.logger.error("SITE_PASSWORD is malformed")
        raise RuntimeError(
            "SITE_PASSWORD must be a password or a dictionary of {email:password}",
        )
    if not app.config.get("SECRET_KEY"):
        app.logger.error("No SECRET_KEY set!")
        raise RuntimeError(
            "you must configure a SECRET_KEY if you want to use SITE_PASSWORD!",
        )
    okendpoints = {
        "login.login_cmd",
        "login.logout_cmd",
        "static",
    }

    public = app.config.get("PUBLIC_ENDPOINTS")
    if public is not None:
        if isinstance(public, str):  # pragma: no cover
            public = [public]
        okendpoints |= set(public)

    @app.before_request
    def check_login() -> Response | None:
        if request.endpoint in okendpoints:
            return None

        if current_user.is_authenticated:
            return None

        def topath() -> str:
            fp = request.full_path
            if fp.endswith("?"):
                return fp[:-1]
            return fp

        return cast(Response, redirect(url_for("login.login_cmd", next=topath())))

    app.register_blueprint(login, url_prefix=url_prefix)
