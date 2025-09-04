from __future__ import annotations

import re
import tomllib
from abc import ABC
from abc import abstractmethod
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from os import stat_result
from pathlib import Path
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict

import pandas as pd
from flask import abort
from flask import current_app
from flask import g
from flask import has_request_context
from flask import request
from flask import Response
from flask import send_file
from flask import url_for
from protein_turnover.jobs import TurnoverJob
from protein_turnover.plotting import plot_all
from protein_turnover.sqla.query import Column
from protein_turnover.sqla.query import dict_to_form_filter
from protein_turnover.sqla.query import DTQuery
from protein_turnover.sqla.query import FormFilter
from protein_turnover.sqla.query import RowFilter
from protein_turnover.sqla.query import RowQuery

from .jobs import get_jobs_manager
from .jobsmanager import Locator

# from protein_turnover.plotting import enrichment_plot


class DataTableColumn(TypedDict):
    data: str
    title: str
    className: NotRequired[str]


class DataTableAjax(TypedDict):
    url: str
    type: Literal["POST", "GET"]


class DataTableLang(TypedDict):
    info: str


# see DataTables.Settings in node_modules/@types/datatables.net/index.d.ts
class DataTableSettings(TypedDict):
    processing: bool
    serverSide: bool
    select: Literal["single", "multiple"]
    dom: str
    pageLength: int
    columns: list[DataTableColumn]
    scrollX: bool
    ajax: NotRequired[DataTableAjax]
    data: NotRequired[list[dict[str, Any]]]
    language: NotRequired[DataTableLang]
    order: NotRequired[list[tuple[int, str]]]


class DTPepData(TypedDict):
    data: list[dict[str, Any]]
    lpf: str | None  # extra data see inspect.ts


# see AjaxData in index.d.ts
class DTReply(TypedDict):
    draw: int
    recordsTotal: int
    recordsFiltered: int
    data: list[dict[str, Any]]
    total_peptides: int  # extra... (see inspect.ts)


@dataclass
class DataTable(ABC):
    dataid: str
    columns: list[Column]

    view: str | None = "inspect.ajax"
    search: bool = False
    want_filter: bool = True
    index_col: str = "result_index"

    def locator(self) -> Locator:
        return get_jobs_manager().locate_from_url(self.dataid)

    def locate(self) -> Path:
        """Find (possible) sqlite file for this dataid"""
        return self.locator().locate_data_file()

    def get_config(self) -> TurnoverJob:
        cf = self.locator().locate_config_file()
        if not cf.exists():  # pragma: no cover
            abort(404)
        return TurnoverJob.restore(cf)

    def stat(self) -> stat_result:  # pragma: no cover
        return self.locate().stat()

    @abstractmethod
    def get_datatable_df(
        self,
        rows: RowFilter | None = None,
    ) -> pd.DataFrame | None:  # pragma: no cover
        raise NotImplementedError()

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def url(self) -> str:
        if self.view is None:
            raise RuntimeError("no view!")
        return url_for(self.view, dataid=self.dataid)

    def get_view_columns(self) -> list[Column]:
        return [c for c in self.columns if c.view]

    def dt_config(self, page_length: int | None = None) -> DataTableSettings:
        # called by view
        return datatable_config_serverside(
            self.get_view_columns(),
            self.url(),
            page_length,
        )

    def get_datatable_query(self) -> DTQuery | None:
        return paging_from_request()

    def get_filter(self) -> FormFilter | None:
        return filter_from_request()

    def get_plot_row(self, index: int) -> RowFilter:
        return RowFilter([RowQuery(self.index_col, "=", index)])

    def plot_all(
        self,
        index: int,
        image_format: str = "png",
        figsize: tuple[float, float] = (5.0, 12.0),
        *,
        layout: tuple[int, int] = (4, 1),
        enrichmentColumns: int = 0,
    ) -> tuple[BytesIO, pd.Series] | None:
        # called by view

        start = datetime.now()
        df = self.get_datatable_df(self.get_plot_row(index))
        if df is None:  # pragma: no cover
            return None
        df = self.rehydrate(df)
        assert len(df) == 1, len(df)
        row = df.iloc[0]
        settings = self.get_config().settings

        end = datetime.now()
        fig, *_ = plot_all(
            row,  # type: ignore
            settings,
            figsize=figsize,
            hspace=0.5,
            layout=layout,
            enrichmentColumns=enrichmentColumns,
        )
        out = BytesIO()
        fig.savefig(out, format=image_format)
        out.seek(0)

        current_app.logger.debug(
            "plot: fetch df=%s plot=%s",
            end - start,
            datetime.now() - end,
        )
        return out, row

    def encode_img(self, img: BytesIO, image_format: str = "png") -> str:
        return encode_img(img, image_format)

    def set_download_cookie(self, resp: Response) -> None:
        # browser javascript will look for cookie... to end
        # ui feedback wait
        resp.set_cookie(
            "fileDownload",
            value="true",
            max_age=20,
            path="/",
            httponly=False,
        )

    def send_pdf(
        self,
        rowid: int,
        image_format: str = "pdf",
        *,
        enrichmentColumns: int = 0,
        layout: tuple[int, int] = (4, 1),
    ) -> Response:
        # called by view
        data = self.plot_all(
            rowid,
            image_format=image_format,
            enrichmentColumns=enrichmentColumns,
            layout=layout,
        )

        if data is None:  # pragma: no cover
            abort(404)
        assert data is not None
        plot, s = data
        mt = "application" if image_format == "pdf" else "image"
        resp = send_file(
            plot,
            mimetype=f"{mt}/{image_format}",
            as_attachment=True,
            download_name=f"plot-{s.peptide}-{rowid}.{image_format}",  # type: ignore
        )
        self.set_download_cookie(resp)
        return resp


@dataclass
class PeptideTable(DataTable):
    view: str | None = None  # no serverside
    group: int = 0
    with_data: bool = False
    group_col: str = "group_number"
    order_col: str = "peptide"

    def filter_peptides(self) -> bool:  # from web page
        if not has_request_context():  # pragma: no cover
            return False

        if not self.want_filter:  # pragma: no cover
            return False

        if "exclude" in request.values:
            return request.values["exclude"] == "true"

        if "filter-peptides" in request.form:
            return request.form["filter-peptides"] == "true"

        return False

    def dt_config(self, page_length: int | None = None) -> DataTableSettings:
        # called by view
        view_columns = [c for c in self.columns if c.view and c.send]
        data = None
        jsonresult = None
        extra = None
        if self.with_data:
            jsonresult = self.peptide_data()
            if jsonresult is not None:
                data = jsonresult["data"]
                extra = {"lpf": jsonresult["lpf"]}
                if data:
                    view_columns = [c for c in view_columns if c.name in data[0]]

        ret = datatable_config(
            view_columns,
            self.url() if self.view is not None else None,
            with_search=self.search,
            length=page_length,
            data=data,
            extra=extra,  # add lpf
        )
        ret.update(
            {
                "language": {
                    "info": "Showing _START_ to _END_ of _TOTAL_ Peptides",
                },
            },
        )
        order_col = list(
            filter(lambda v: v[1].name == self.order_col, enumerate(view_columns)),
        )
        if order_col:
            ret.update({"order": [(order_col[0][0], "asc")]})
        return ret

    def url(self) -> str:  # pragma: no cover
        assert self.view is not None
        return url_for(self.view, dataid=self.dataid, group=self.group)

    @abstractmethod
    def peptide_data(self) -> DTPepData | None:  # pragma: no cover
        raise NotImplementedError()


def datatable_config_serverside(
    columns: list[Column],
    url: str,
    length: int | None = None,
    item_name: str = "Proteins",
) -> DataTableSettings:
    """Config for serverside datatables.net $('#id').DataTables({config})"""
    # https://datatables.net/reference/option/dom
    dom = """<'row'<'col-12'i>>
    <'row'<'col-12'p>>
    <'row'<'col-sm-12 col-md-6'f><'col-sm-12 col-md-6'l>>
    <'row'<'col-12'tr>>"""

    def dt(c: Column) -> DataTableColumn:
        ret: DataTableColumn = {"data": c.name, "title": c.title}
        if c.className is not None:  # pragma: no cover
            ret["className"] = c.className
        return ret

    return {
        "processing": True,  # show processing popup in browser
        "serverSide": True,  # we will do data
        "select": "single",
        "dom": dom,
        "pageLength": length if length else 10,
        "ajax": {"url": url, "type": "POST"},
        "columns": [dt(c) for c in columns],
        "scrollX": True,
        "language": {
            "info": f"Showing _START_ to _END_ of _TOTAL_ {item_name}",
        },
    }


def datatable_config(
    columns: list[Column],
    url: str | None,
    with_search: bool = True,
    length: int | None = None,
    data: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> DataTableSettings:
    # https://datatables.net/reference/option/dom

    def dt(c: Column) -> DataTableColumn:
        ret: DataTableColumn = {"data": c.name, "title": c.title}
        if c.className is not None:
            ret["className"] = c.className
        return ret

    dom_with_search = """<'row'<'col-12'i>>
    <'row'<'col-12'p>>
    <'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>
    <'row'<'col-12'tr>>"""
    dom = """<'row'<'col-12'i>>
    <'row'<'col-12'p>>
    <'row'<'col-12'tr>>"""
    ret: DataTableSettings = {
        "processing": False,
        "serverSide": False,
        "select": "single",
        "dom": dom_with_search if with_search else dom,
        "pageLength": length if length else 10,
        "columns": [dt(c) for c in columns],
        "scrollX": True,
    }
    if data is None:
        if url is None:  # pragma: no cover
            raise RuntimeError("must specifiy either data or url")
        ret["ajax"] = {"url": url, "type": "POST"}

    else:
        ret["data"] = data
    if extra is not None:
        ret.update(extra)  # type: ignore
    return ret


def paging_from_request() -> DTQuery | None:
    if not has_request_context():  # pragma: no cover
        return None
    if hasattr(g, "dtquery"):
        return g.dtquery
    d = request.values
    draw, start, length, search, search_re, ascending, col_num = (
        int(d["draw"]),
        int(d["start"]),
        int(d["length"]),
        d["search[value]"],
        d["search[regex]"] == "true",
        d["order[0][dir]"] == "asc",
        int(d["order[0][column]"]),
    )
    order_column = d[f"columns[{col_num}][data]"]

    ret = DTQuery(
        start=start,
        length=length,
        search=search.strip() if search != "" else None,
        regex=search_re,
        ascending=ascending,
        order_column=order_column,
        draw=draw,
    )
    g.dtquery = ret
    return ret


def paging_from_form() -> DTQuery | None:
    import json

    if not has_request_context():  # pragma: no cover
        return None
    d = request.form
    if "searchinfo" not in d:
        return None
    value = d["searchinfo"]
    if value == "":
        return None
    v = json.loads(value)
    return DTQuery(
        order_column=v["order_column"],
        search=v["search"],
        ascending=v["ascending"],
        length=-1,
    )


FILTER = re.compile(r"^filters\[(.*)\]$")


def filter_match(k: str) -> str | None:
    m = FILTER.match(k)
    if m:
        return m.group(1)
    return None


def filter_from_request() -> FormFilter | None:
    if not has_request_context():  # pragma: no cover
        return None
    if hasattr(g, "filtered"):  # pragma: no cover
        return g.filtered
    try:
        g.filtered = sqlfilter = dict_to_form_filter(request.values, filter_match)
        return sqlfilter
    except ValueError:  # pragma: no cover
        g.filtered = None
        return None


def filter_from_form() -> FormFilter | None:
    if not has_request_context():  # pragma: no cover
        return None
    if hasattr(g, "filtered"):  # pragma: no cover
        return g.filtered
    try:
        g.filtered = sqlfilter = dict_to_form_filter(request.form, lambda s: s)
    except ValueError:  # pragma: no cover
        g.filtered = None
        return None
    return sqlfilter


def encode_img(img: BytesIO, image_format: str = "png") -> str:
    data = f"data:image/{image_format};base64,".encode("ascii") + b64encode(img.read())
    return data.decode("ascii")


def get_columns(filename: str) -> list[Column] | None:  # pragma: no cover
    try:
        with current_app.open_instance_resource(filename, mode="rb") as fp:
            ret = [Column(**cols) for cols in tomllib.load(fp)["Column"]]  # type: ignore

        current_app.logger.info(
            'read columns file: "%s" from instance directory',
            filename,
        )
        return ret
    except Exception:
        return None
