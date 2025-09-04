from __future__ import annotations

import re

import click
from flask.cli import AppGroup

turover_cli = AppGroup("turnover", help=click.style("Turnover commands", fg="magenta"))


@turover_cli.command("running")
def running_cmd() -> None:
    """Show running and pending jobs"""
    from .jobs import get_jobs_manager, get_bg_client

    is_running = get_bg_client().is_running()
    jm = get_jobs_manager()
    jobs = jm.find_jobs()
    running = jobs["running"]
    queued = jobs["queued"]
    finished = jobs["finished"]
    status = "running" if is_running else "not runnning"
    click.secho(
        f"background queue is {status} @ {jm.jobsdir_list[0]}.",
        fg="green" if is_running else "red",
    )
    click.secho(
        f"running: {len(running)}, queued: {len(queued)}, finished: {len(finished)}",
    )


BLOCK = re.compile("<code>math(?:\n)?(.*?)</code>", re.MULTILINE | re.DOTALL)
INLINE = re.compile(r"\$<code>(.*?)</code>\$", re.MULTILINE | re.DOTALL)


@turover_cli.command("about")
@click.option(
    "--no-github",
    is_flag=True,
    help="write out block equations with $$ as delimeters",
)
@click.option("--out", type=click.Path(dir_okay=False))
def about(no_github: str, out: str | None) -> None:
    """Generate Calculations.md markdown"""
    from flask import render_template, current_app
    from pathlib import Path
    import markdown  # type: ignore

    if no_github and out is None:
        raise ValueError("choose a filename (--out) for --no-github")
    ret = render_template(
        "about.md.tplt",
        no_github=no_github,
        image_prefix="protein_turnover_website",
    )
    ret = ret.strip() + "\n"
    outn = out or "Calculations.md"
    click.secho(f"writing: {outn}", fg="blue")
    with open(outn, "w", encoding="utf8") as fp:
        fp.write(ret)

    if not no_github and out is None:
        ret = render_template("about.md.tplt", no_github=False, image_prefix="")

        # convert to html
        ret = markdown.markdown(ret)

        # fixup ```math markdown
        ret = BLOCK.sub(r"$$\1$$", ret)
        ret = INLINE.sub(r"$`\1`$", ret)
        ret = ret.strip() + "\n"

        html = Path(current_app.root_path) / "templates" / "about-frag.html"
        click.secho(f"writing: {html}", fg="blue")
        with open(html, "w", encoding="utf8") as fp:
            fp.write(ret)
