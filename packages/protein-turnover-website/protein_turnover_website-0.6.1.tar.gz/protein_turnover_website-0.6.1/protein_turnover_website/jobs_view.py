from __future__ import annotations

from dataclasses import replace
from typing import Literal
from typing import NotRequired
from typing import TypedDict

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import get_template_attribute
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from flask_login import current_user
from protein_turnover.jobs import TurnoverJob
from protein_turnover.pepxml import count_spectra
from protein_turnover.pepxml import scan_pp_probability
from protein_turnover.protxml import scan_proteins
from protein_turnover.pymz import scan_mzml_spectra
from protein_turnover.utils import get_element_names
from protein_turnover.utils import get_isotope_numbers
from protein_turnover.utils import PeptideSettings

from .explorer.explorer import find_directory_from_request
from .explorer.explorer import find_explorer
from .explorer.explorer import get_mountpoints
from .flask_utils import oktokill
from .jobs import ensure_cachedir
from .jobs import ensure_jobsdir
from .jobs import File
from .jobs import get_bg_client
from .jobs import get_jobs_manager
from .jobs import job_from_form
from .jobs import oktokill_abort
from .jobs import remap_job
from .jobs import sanitize
from .jobs import verify_files
from .utils import read_log


job = Blueprint("job", __name__)


class JsonReply(TypedDict):
    status: Literal["OK", "failed"]
    msg: str
    dataid: NotRequired[str]


NoneJob = TurnoverJob(
    job_name="",
    pepxml=[],
    protxml="",
    mzmlfiles=[],
    jobid="",
    settings=PeptideSettings(),
    email="",
)


@job.route("/job-index")
def index() -> str:
    """Jobs table"""
    return render_template(
        "job-index.html",
        is_running=get_bg_client().is_running(),
        **get_jobs_manager().find_jobs(),
        oktokill=oktokill(),
    )


@job.route("/refresh-jobs")
def refresh_jobs() -> Response:
    """Refresh jobtables: returns json {table:html}"""

    jobs = get_jobs_manager().find_jobs()  # pylint: disable=redefined-outer-name
    jobtable = get_template_attribute("job-macros.html", "jobtable")
    ok = oktokill()
    jt = {k: jobtable(v, ok) for k, v in jobs.items()}
    return jsonify(jt)


@job.route("/meta")
def find_metadata() -> str:
    """Find TurnoverJob file and return rendered HTML"""

    dataid = request.values.get("dataid")
    if not dataid:  # pragma: no cover
        abort(404)
    meta = get_jobs_manager().locate_from_url(dataid).locate_config_file()

    if not meta.exists():  # pragma: no cover
        abort(404)
    jobdata = TurnoverJob.restore(meta)
    jobdata = remap_job(jobdata)
    showjob = get_template_attribute("job-macros.html", "showjob")
    tj, located = sanitize(jobdata)
    return showjob(tj, dataid, located)


@job.route("/log")
def find_log() -> str:
    """Show log data"""

    dataid = request.values.get("dataid")
    if not dataid:  # pragma: no cover
        abort(404)
    mountpoints = get_mountpoints()
    logfile = get_jobs_manager().locate_from_url(dataid).locate_log_file()

    if not logfile.exists():  # pragma: no cover
        results = []
    else:
        n: int = current_app.config["LOG_READ"]
        results = list(reversed(list(read_log(logfile, start=-n))))[:100]
        results = mountpoints.sanitize_log(results)

    showlog = get_template_attribute("job-macros.html", "showlog")
    return showlog(results)


@job.route("/create-job-page")
def create_job_page() -> str:
    """Create Jobs Table"""

    mountpoints = get_mountpoints()
    explorer = find_explorer(mountpoints)

    if explorer is None:  # pragma: no cover
        abort(404)

    turnover_job = NoneJob

    dataid = request.values.get("dataid")
    message = ""
    if dataid:
        jobpath = get_jobs_manager().locate_from_url(dataid).locate_config_file()
        if jobpath.exists():
            try:
                turnover_job = TurnoverJob.restore(jobpath)
                turnover_job = remap_job(turnover_job)
                turnover_job, missing = verify_files(turnover_job)
                if missing:
                    message = f'Some of the original files from job <i>"{turnover_job.job_name}"</i>: (<code>{", ".join(missing)}</code>) could not be found!'
                turnover_job = replace(turnover_job, job_name="")
            except Exception as e:  # pragma: no cover
                current_app.logger.error("can't read toml for %s [%s]", dataid, e)

    if current_user.is_authenticated:
        turnover_job = replace(turnover_job, email=current_user.email or "")

    allow_links = current_app.config["ALLOW_LINKS"]
    return render_template(
        "create-job.html",
        mountpoints=mountpoints,
        explorer=explorer,
        message=message,
        elements=get_element_names(),
        atomicProperties=get_isotope_numbers(),
        job=turnover_job,
        pepxmlfiles=File.from_files(turnover_job.pepxml, allow_links),
        protxmlfile=File.from_files(
            [turnover_job.protxml] if turnover_job.protxml else [],
            allow_links,
        ),
        mzmlfiles=File.from_files(turnover_job.mzmlfiles, allow_links),
        is_running=get_bg_client().is_running(),
    )


@job.route("/create_job", methods=["POST"])
def create_job() -> Response:
    jobname = request.form.get("job_name", "").strip()
    if len(jobname) < 6:
        return jsonify(
            JsonReply(
                status="failed",
                msg="can't create job without a jobname with length >=6",
            ),
        )
    jm = get_jobs_manager()

    # try to get a unique id starting with possible jobname
    jobid = jm.prefix_jobid(jobname)

    jobby = job_from_form(jobid)
    jd = jm.locate_from_new(jobid).locate_directory()
    try:
        jd.mkdir(exist_ok=True, parents=True)
    except OSError as e:  # pragma: no cover
        current_app.logger.error("failed to make directory: %s reason: %s", jd, e)
        return jsonify(
            JsonReply(
                status="failed",
                msg=f"can't create job {jobby.jobid}: {e}",
                dataid=jobby.jobid,
            ),
        )
    jobby = replace(jobby, status="pending")
    jobby.save_to_dir(jd)
    # tell background to wake up
    get_bg_client().signal()

    return jsonify(
        JsonReply(status="OK", msg=f"job {jobby.jobid} created", dataid=jobby.jobid),
    )


@job.route("/kill")
def kill_job() -> Response:
    dataid = request.values.get("dataid")
    if not dataid:  # pragma: no cover
        abort(404)

    oktokill_abort()

    msg = get_jobs_manager().locate_from_url(dataid).kill_pid()
    if msg is not None:
        return jsonify(JsonReply(status="failed", msg=msg, dataid=dataid))

    return jsonify(JsonReply(status="OK", msg=f"job {dataid} killed", dataid=dataid))


@job.route("/restart")
def restart_job() -> Response:
    dataid = request.values.get("dataid")
    if not dataid:  # pragma: no cover
        abort(404)

    oktokill_abort()

    config = get_jobs_manager().locate_from_url(dataid).locate_config_file()
    if not config.exists():
        return jsonify(
            JsonReply(status="failed", msg=f"no job {dataid}!", dataid=dataid),
        )

    job = TurnoverJob.restore(config)  # pylint: disable=redefined-outer-name
    job = remap_job(job)
    job = replace(job, status="pending")

    job.save_file(config)
    get_bg_client().signal()
    return jsonify(JsonReply(status="OK", msg=f"job {dataid} queued for processing"))


@job.route("/delete")
def remove_job() -> Response:
    dataid = request.values.get("dataid")
    if not dataid:  # pragma: no cover
        abort(404)

    oktokill_abort()

    try:
        ok = get_jobs_manager().locate_from_url(dataid).remove()

        if not ok:
            return jsonify(JsonReply(status="failed", msg=f"no job {dataid}!"))

        return jsonify(JsonReply(status="OK", msg=f"job {dataid} removed"))
    except Exception as e:  # pragma: no cover
        current_app.logger.error("can't remove job %s, reason=%s", dataid, e)

    return jsonify(JsonReply(status="failed", msg=f"can't remove job {dataid}"))


@job.route("/check-pepxml")
def check_pepxml() -> Response:
    pepxmls = request.values.getlist("pepxmls[]")
    if not pepxmls:
        abort(404)

    mountpoints = get_mountpoints()

    explorer = find_directory_from_request(mountpoints)
    if explorer is None:
        abort(404)

    pepxml_dir_path = explorer.directory(mountpoints)
    if pepxml_dir_path is None:
        abort(404)
    res: dict[str, int] = {}
    has_pp: list[bool] = []
    for pepxml in pepxmls:
        pepxml_path = pepxml_dir_path.joinpath(pepxml)
        if not pepxml_path.exists():  # pragma: no cover
            abort(404)
        has_pp.append(scan_pp_probability(pepxml_path))

        ret = count_spectra(pepxml_path)
        for k, v in ret.items():
            res[k] = res.get(k, 0) + v
    if sum(res.values()) == 0:  # pragma: no cover
        return jsonify(JsonReply(status="failed", msg="No spectra found!"))

    return jsonify({"status": "OK", "counts": res, "has_peptide_prophet": all(has_pp)})


@job.route("/check-mzml")
def check_mzml() -> Response:
    mzmls = request.values.getlist("mzml[]")
    if not mzmls:  # pragma: no cover
        abort(404)

    mountpoints = get_mountpoints()

    explorer = find_directory_from_request(mountpoints)
    if explorer is None:
        abort(404)

    path = explorer.directory(mountpoints)
    if path is None:  # pragma: no cover
        abort(404)
    ret: dict[str, int] = {}
    for mzml in mzmls:
        filename = path.joinpath(mzml)
        if not filename.exists():
            abort(404)
        ret[mzml] = sum(1 for _ in scan_mzml_spectra(filename))
    if sum(ret.values()) == 0:
        return jsonify(JsonReply(status="failed", msg="No spectra found!"))
    return jsonify({"status": "OK", "counts": ret})


@job.route("/check-protxml")
def check_protxml() -> Response:
    protxml = request.values.get("protxml")
    if not protxml:  # pragma: no cover
        abort(404)

    mountpoints = get_mountpoints()

    explorer = find_directory_from_request(mountpoints)
    if explorer is None:  # pragma: no cover
        abort(404)

    protxml_path = explorer.directory(mountpoints)
    if protxml_path is None:  # pragma: no cover
        abort(404)

    protxml_path = protxml_path.joinpath(protxml)
    if not protxml_path.exists():  # pragma: no cover
        abort(404)

    proteins = sum(1 for _ in scan_proteins(protxml_path))
    if proteins == 0:
        return jsonify(JsonReply(status="failed", msg="No proteins found!"))
    return jsonify({"status": "OK", "proteins": proteins})


def init_app(app: Flask, url_prefix: str = "/") -> None:
    ensure_jobsdir(app)
    ensure_cachedir(app)
    m = app.config.get("REMAP_MOUNTPOINTS")
    if m and not isinstance(m, dict):  # pragma: no cover
        raise RuntimeError("REMAP_MOUNTPOINTS is not a dictionary")
    app.register_blueprint(job, url_prefix=url_prefix)
