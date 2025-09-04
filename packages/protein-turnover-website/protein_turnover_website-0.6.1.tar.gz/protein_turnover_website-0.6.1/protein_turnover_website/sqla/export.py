from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Literal
from typing import TYPE_CHECKING

import pandas as pd
from flask import abort
from flask import current_app
from flask import request
from flask import Response
from flask import send_file
from protein_turnover.exts import RESULT_EXT
from protein_turnover.sqla.query import Aggregate
from protein_turnover.sqla.query import Column
from protein_turnover.sqla.query import DTQuery
from protein_turnover.sqla.query import RatioAggregate
from typing_extensions import override
from werkzeug.utils import secure_filename

from ..inspect import filter_from_form
from ..inspect import paging_from_form
from .inspect import SQLDataTable


if TYPE_CHECKING:
    from protein_turnover.sqla.query import FormFilter
    from protein_turnover.sqla.query import RowFilter


@dataclass
class SQLExportDataTable(SQLDataTable):
    @override
    def get_filter(self) -> FormFilter | None:
        return filter_from_form()

    @override
    def get_datatable_query(self) -> DTQuery | None:
        return paging_from_form()

    @override
    def get_datatable_df(self, rows: RowFilter | None = None) -> pd.DataFrame | None:
        df = super().get_datatable_df(rows)
        if df is None:  # pragma: no cover
            return None
        # ensure column ordering correct
        send = [c for c in self.columns if c.send and c.name in df.columns]
        ret = df[[c.name for c in send]]
        ret.rename(
            columns={c.name: c.title for c in send if c.title and c.name},
            inplace=True,
        )
        return ret

    def export_tsv(
        self,
        df: pd.DataFrame,
        out: BytesIO,
        compression: Literal["gzip", "zip"] | None = None,
        sep: str = "\t",
    ) -> None:
        df.to_csv(out, compression=compression, index=False, encoding="utf-8", sep=sep)

    def export_xlsx(self, df: pd.DataFrame, out: BytesIO) -> None:
        df.to_excel(out, index=False)

    def send_df(self, df: pd.DataFrame, filename: str, fmt: str = "tsv") -> Response:
        # last_modified = self.locate().stat().st_mtime

        compression: Literal["gzip", "zip"] | None = None
        out = BytesIO()
        if fmt == "tsv":
            if "gzip" in request.accept_encodings:  # pragma: no cover
                compression = "gzip"
            elif "zip" in request.accept_encodings:  # pragma: no cover
                compression = "zip"
            self.export_tsv(df, out, compression)
        else:
            self.export_xlsx(df, out)
        size = out.tell()
        out.seek(0)
        current_app.logger.info("download size %s: %d", filename, size)
        resp = send_file(
            out,
            mimetype="application/vnd.ms-excel",
            as_attachment=True,
            download_name=filename,  # type: ignore
            # last_modified=last_modified
        )
        self.set_encoding(resp, compression)
        # resp.content_length = size
        self.set_download_cookie(resp)
        return resp

    def set_as_attachment(self, resp: Response, filename: str) -> None:
        resp.headers.set("Content-Disposition", "attachment", filename=filename)

    def set_encoding(
        self,
        resp: Response,
        compression: Literal["gzip", "zip"] | None = None,
    ) -> None:
        if compression is not None:  # pragma: no cover
            resp.headers.update(  # type: ignore
                {"Content-Encoding": compression, "Vary": "Accept-Encoding"},
            )

    def send(self, fmt: str = "tsv") -> Response:
        # called by view
        df = self.get_datatable_df()
        if df is None:  # pragma: no cover
            abort(404)
        name = self.get_name()
        return self.send_df(df, f"{name}.{fmt}", fmt=fmt)

    def get_name(self) -> str:
        try:
            job = self.get_config()
            name = secure_filename(job.job_name)
        except OSError:  # pragma: no cover
            name = self.dataid
        return name

    def send_all(self) -> Response:
        # called by view
        data_file = self.locate()
        if not data_file.exists():  # pragma: no cover
            abort(404)
        resp = send_file(
            str(data_file),
            as_attachment=True,
            download_name=self.get_attachment_filename(),  # type: ignore
            mimetype="application/octet-stream",
            conditional=True,
        )
        self.set_download_cookie(resp)
        return resp

    def get_attachment_filename(self) -> str:
        return f"{self.get_name()}{RESULT_EXT}"


EXPORT_COLUMNS = [
    Column("protein_name", title="Protein"),
    Column("protein_description", title="Description"),
    Column("group_number", title="Group", search=False),
    Column("probability", title="Probability"),
    Column(
        "#Peptides",
        aggregate=Aggregate(column="peptideid", aggfunc="count"),
    ),  # virtual
    Column("num_found_peptides", title="#Found Peptides", search=False),
    Column("lpf_std", title="STD LPF", search=False),
    Column(
        "Filtered STD LPF",
        aggregate=Aggregate(column="relativeIsotopeAbundance", aggfunc="std"),
    ),
    Column(
        "nnls_min",
        title="NNLS (min)",
        aggregate=RatioAggregate(column="nnls_residual", aggfunc="min"),
    ),
    Column("Enrichment Avg", aggregate=Aggregate(column="enrichment", aggfunc="avg")),
    Column("lpf_median", title="Median LPF", search=False),
    Column(
        "Filtered Peptides",
        aggregate=Aggregate(column="peptide", aggfunc="group_concat", args=(", ",)),
    ),  # virtual
    Column("unique_stripped_peptides", title="All Peptides", search=False),
    Column(
        "PP Probability Avg",
        aggregate=Aggregate(column="peptideprophet_probability", aggfunc="avg"),
    ),
]


def make_export_table(dataid: str) -> SQLExportDataTable:
    columns: list[Column] = current_app.config.get("EXPORT_COLUMNS") or EXPORT_COLUMNS
    return SQLExportDataTable(
        dataid,
        columns=columns,
        index_col="proteinid",
    )
