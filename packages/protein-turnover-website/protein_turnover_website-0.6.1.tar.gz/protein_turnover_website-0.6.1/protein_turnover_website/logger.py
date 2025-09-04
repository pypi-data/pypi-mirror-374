from __future__ import annotations

import logging
import time
from logging import Formatter
from logging import LogRecord
from logging.handlers import SMTPHandler

from flask import Flask
from flask import has_request_context
from flask import request


def remote_addr() -> str | None:
    # try CloudFlare
    addr = request.headers.get("CF-Connecting-IP")
    if addr:  # pragma: no cover
        return addr
    addr = request.headers.get("X-Forwarded-For")
    if addr:  # pragma: no cover
        return addr
    return request.remote_addr


def escapeit(url: str) -> str:
    # because microsoft mangles urls
    if not url:  # pragma: no cover
        return ""
    return url.replace("https://", "").replace("http://", "")


class RequestFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        ret = super().format(record)
        if not has_request_context():
            return ret

        extra = f"""
Remote Address:       {remote_addr()}
Request Path:         {request.path}
Request Values:       {request.values}
Request User-Agent:   {request.user_agent}
Original Referrer:    {escapeit(request.referrer) if request.referrer is not None else "<unknown>"}
Request Referrer:     {request.referrer}

"""
        return extra + ret


class LimitFilter(logging.Filter):
    def __init__(self, delay: int = 60 * 5):  # pragma: no cover
        super().__init__("delay")
        self.start: float | None = None
        self.delay = delay

    def filter(self, record: LogRecord) -> bool:  # pragma: no cover
        t = time.time()
        if self.start is None or (t - self.start) > self.delay:
            self.start = t
            return True
        return False


def init_email_logger(
    app: Flask,
    level: int = logging.ERROR,
) -> None:
    admins: str | list[str] | None = app.config.get("ADMINS")
    if not admins:
        return
    mailhost: str | None | tuple[str, int] = app.config.get("LOG_MAIL_SERVER")
    if mailhost is None or (
        isinstance(mailhost, str) and mailhost == "none"
    ):  # pragma: no cover
        return
    if isinstance(admins, str):
        admins = [admins]

    frm = admins[0].split("@")[-1]
    name = app.config.get("MAIL_SUBJECT", app.name)
    if isinstance(mailhost, str) and ":" in mailhost:
        mailhost, port = mailhost.rsplit(":", maxsplit=1)
        mailhost = (mailhost, int(port))

    mail_handler = SMTPHandler(
        mailhost,
        app.name + f"-server-error@{frm}",
        admins,
        subject=name + " Failed",
    )

    mail_handler.setLevel(level)

    delay = app.config.get("LOG_ERROR_DELAY")

    if delay is not None and delay > 0:  # pragma: no cover
        mail_handler.addFilter(LimitFilter(delay=delay))

    mail_handler.setFormatter(
        RequestFormatter(
            """
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
""",
        ),
    )

    app.logger.addHandler(mail_handler)
