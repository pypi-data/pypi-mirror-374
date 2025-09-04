from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING

import pandas as pd
from flask import after_this_request
from flask import current_app
from flask import g
from flask import Response
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from protein_turnover.plotting import enrichment_plot
from protein_turnover.plotting import nnls_plot
from protein_turnover.plotting import plotLPF
from protein_turnover.plotting import to_image_url
from protein_turnover.sqla.query import Aggregate
from protein_turnover.sqla.query import all_plotting_columns
from protein_turnover.sqla.query import Column
from protein_turnover.sqla.query import PeptideQuery
from protein_turnover.sqla.query import ProteinQuery
from protein_turnover.sqla.query import RatioAggregate
from protein_turnover.sqla.query import RowFilter
from protein_turnover.sqla.query import RowQuery
from protein_turnover.sqla.query import SimplePeptideQuery
from protein_turnover.sqla.utils import file2engine
from sqlalchemy.engine import Engine
from typing_extensions import override

from ..inspect import DataTable
from ..inspect import DTPepData
from ..inspect import DTReply
from ..inspect import PeptideTable
from ..utils import round_df

if TYPE_CHECKING:
    from protein_turnover.sqla.query import ProteinQueryResult


def get_figure(ax: Axes) -> Figure:
    ret = ax.get_figure()
    assert isinstance(ret, Figure)
    return ret


class EngineMixin:
    dataid: str

    def get_engine(self) -> Engine | None:
        if not hasattr(g, "engines"):
            g.engines = {}

        engine = g.engines.get(self.dataid)  # type: ignore
        if engine is not None:  # pragma: no cover
            return engine

        db = self.locate()  # type: ignore
        if not db.is_file():
            return None

        echo = current_app.debug and current_app.config["ECHO_QUERY"]
        engine = g.engines[self.dataid] = file2engine(db, echo=echo)
        # engine.echo = False

        @after_this_request
        def dispose(response: Response) -> Response:
            engine.dispose()
            return response

        return engine


class SQLDataTable(DataTable, EngineMixin):
    group_col: str = "group_number"

    @override
    def get_datatable_df(self, rows: RowFilter | None = None) -> pd.DataFrame | None:
        result = self.full_query(rows, want_all=False)
        if result is None:
            return None
        return result.result_df

    def full_query(
        self,
        rows: RowFilter | None = None,
        want_all: bool = True,
    ) -> ProteinQueryResult | None:
        engine = self.get_engine()
        if engine is None:  # pragma: no cover
            return None
        dtquery = self.get_datatable_query()

        sqlafilter = self.get_filter() if self.want_filter else None

        pq = ProteinQuery(sqlafilter, rows, dtquery=dtquery, columns=self.columns)
        result = pq.query(engine, want_all=want_all)
        return result

    def query(self) -> DTReply | None:
        result = self.full_query()
        if result is None:
            return None

        df = result.result_df
        df.fillna(0.0, inplace=True)

        if self.index_col in df.columns:
            df.rename(columns={self.index_col: "DT_RowId"}, inplace=True)
            # df['DT_RowId'] = df['DT_RowId'].apply(str)

        else:  # pragma: no cover
            df.index.name = "DT_RowId"
            df.reset_index(inplace=True)

        roundfloat = round_df(df)

        dtquery = self.get_datatable_query()
        return DTReply(
            draw=dtquery.draw if dtquery else 0,
            recordsTotal=result.total_proteins,
            recordsFiltered=result.total_filtered,
            total_peptides=result.total_peptides,
            data=[
                roundfloat(d)
                for d in df.to_dict("records")  # pylint: disable=not-an-iterable
            ],
        )


class SQLPeptideTable(PeptideTable, EngineMixin):
    @override
    def get_datatable_df(self, rows: RowFilter | None = None) -> pd.DataFrame | None:
        engine = self.get_engine()
        if engine is None:  # pragma: no cover
            return None
        filt = self.get_filter()
        rf = RowFilter([RowQuery(self.group_col, "=", self.group)])
        filtered_column = None
        if not self.filter_peptides() and "filtered" in [c.name for c in self.columns]:
            filtered_column = "filtered"
        rows = rows.add(rf) if rows else rf

        pdq = PeptideQuery(
            filt,
            rows,
            columns=self.columns,
            filtered_column=filtered_column,
        )

        start = datetime.now()

        df = pdq.query(
            engine,
        )

        df = self.rehydrate(df)
        current_app.logger.debug(
            "read: %s[%d] %s",
            self.dataid,
            len(df),
            datetime.now() - start,
        )

        return df

    def peptide_data(self) -> DTPepData | None:
        # called by view

        df = self.get_datatable_df()
        if df is None:  # pragma: no cover
            return None
        if "filtered" in df:
            df["filtered"] = df["filtered"].map(lambda passed: "✓" if passed else "⨯")

        if self.index_col in df.columns:
            df.rename(columns={self.index_col: "DT_RowId"}, inplace=True)
        else:  # pragma: no cover
            df.index.name = "DT_RowId"
            df.reset_index(inplace=True)
        # need this since np.nan will be "jsonized" to NaN!
        df.fillna(0.0, inplace=True)

        roundfloat = round_df(df)

        ret: DTPepData = DTPepData(
            data=[roundfloat(d) for d in df.to_dict("records")],
            lpf=self.get_lpf(df),
        )

        return ret

    def get_lpf(self, df: pd.DataFrame) -> str | None:
        if len(df) == 0:  # pragma: no cover
            return None
        if "relativeIsotopeAbundance" not in df.columns:
            return None
        fig = plotLPF(df).get_figure()
        assert isinstance(fig, Figure)
        return to_image_url(fig)


class SQLSimplePeptideQueryTable(DataTable, EngineMixin):
    @override
    def get_datatable_df(
        self,
        rows: RowFilter | None = None,
    ) -> pd.DataFrame | None:
        engine = self.get_engine()
        if engine is None:  # pragma: no cover
            return None
        start = datetime.now()
        # engine.echo = True
        filt = self.get_filter() if self.want_filter else None
        spd = SimplePeptideQuery(rows, filt, columns=self.columns)
        df = spd.query(engine)

        current_app.logger.debug(
            "read: %s[%d] %s",
            self.dataid,
            len(df),
            datetime.now() - start,
        )
        return df


PROTEIN_COLUMNS = [
    Column("group_number", title="Group", search=False),
    Column("protein_name", title="Protein"),
    Column("protein_description", title="Description"),
    Column(
        "num_peptides",
        title="#Peptides",
        aggregate=Aggregate(column="peptideid", aggfunc="count"),
    ),  # virtual
    Column(
        "nnls_min",
        title="NNLS (min)",
        aggregate=RatioAggregate(column="nnls_residual", aggfunc="min"),
    ),
    Column("num_found_peptides", title="#Found Peptides", search=False),
    Column(
        "lpf_std",
        title="STD LPF",
        aggregate=Aggregate(column="relativeIsotopeAbundance", aggfunc="std"),
        search=False,
    ),
    Column(
        "lpf_median",
        title="Median LPF",
        aggregate=Aggregate(column="relativeIsotopeAbundance", aggfunc="median"),
        search=False,
    ),
    Column("proteinid", view=False, search=False),
]


def make_protein_table(dataid: str) -> SQLDataTable:
    columns: list[Column] = current_app.config.get("PROTEIN_COLUMNS") or PROTEIN_COLUMNS
    return SQLDataTable(
        dataid,
        columns=columns,
        index_col="proteinid",
    )


PEPTIDE_COLUMNS = [
    Column("peptideid", view=False),
    Column("filtered", read=False, title="Passed Filter?"),
    Column("peptide", title="Peptide", className="fixed"),
    Column("modcol", title="Modifications"),
    Column("peptideprophet_probability", title="PP Probability"),
    Column("enrichment", title="Enrichment"),
    Column("nnls_residual", title="NNLS Deviance", denom="totalNNLSWeight"),
    Column("relativeIsotopeAbundance", title="LPF"),
    Column("heavyCor", title="Heavy Correlation"),
    # Column("totalNNLSWeight", send=False),
    Column("protein_names", title="Protein Names"),
]


def make_peptide_table(
    dataid: str,
    group: int,
    with_data: bool = True,
) -> SQLPeptideTable:
    columns: list[Column] = current_app.config.get("PEPTIDE_COLUMNS") or PEPTIDE_COLUMNS
    return SQLPeptideTable(
        dataid,
        columns=columns,
        group=group,
        with_data=with_data,
        index_col="peptideid",
        order_col="peptide",
    )


def make_enrichment_plot(
    dataid: str,
    figsize: tuple[float, float] | None = None,
    column: str = "enrichment",
) -> str | None:
    dt = SQLSimplePeptideQueryTable(
        dataid,
        columns=[
            Column(column),
        ],
        want_filter=True,
    )
    df = dt.get_datatable_df()
    if df is None:  # pragma: no cover
        return None

    if figsize is None:
        dpi = 96
        figsize = (600 / dpi, 400 / dpi)
    ax = enrichment_plot(df, figsize=figsize, column=column)
    fig = get_figure(ax)  # pylint: disable=no-member
    assert fig is not None
    out = BytesIO()
    fig.savefig(out, format="png")
    out.seek(0)
    return dt.encode_img(out, image_format="png")


def get_engine(dataid: str) -> Engine | None:
    return SQLDataTable(dataid, []).get_engine()


def make_nnls_plot(
    dataid: str,
    figsize: tuple[float, float] | None = None,
    percent: float = 0.01,
    scale_intensity: bool = False,
) -> str | None:
    dt = SQLSimplePeptideQueryTable(
        dataid,
        columns=[
            Column(
                "nnls_residual",
                denom="totalIntensityWeight" if scale_intensity else "totalNNLSWeight",
            ),
        ],
        want_filter=True,
    )
    df = dt.get_datatable_df()
    if df is None:
        return None
    if figsize is None:
        dpi = 96
        figsize = (600 / dpi, 400 / dpi)
    ax = nnls_plot(df[["nnls_residual"]], figsize=figsize, percent=percent)
    fig = get_figure(ax)
    if fig is None:  # pragma: no cover
        return None
    fig.tight_layout()
    out = BytesIO()
    fig.savefig(out, format="png")
    out.seek(0)
    return dt.encode_img(out, image_format="png")


def make_plot_table(dataid: str) -> SQLSimplePeptideQueryTable:
    return SQLSimplePeptideQueryTable(
        dataid,
        columns=all_plotting_columns(),
        want_filter=False,
        index_col="peptideid",
    )
