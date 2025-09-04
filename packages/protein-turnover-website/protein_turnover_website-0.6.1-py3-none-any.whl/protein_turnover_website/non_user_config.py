from __future__ import annotations

APP_NAME = "Protein Turnover"
# add iso_peaks_nr_<n> columns if necessary....
FIXSQLITE = False

# we a running a single user website (via turnover web)
WEBSITE_STATE = "multi_user"

# if SITE_PASSWORD is set these are the endpoints that are still public...
PUBLIC_ENDPOINTS = [
    "view.index",
    "inspect.about",
    # "view.configuration",
]
# https://matplotlib.org/stable/api/matplotlib_configuration_api.html#matplotlib
# non-interactive backends: agg, cairo, pdf, pgf, ps, svg, template
MATPLOTLIB_BACKEND = "agg"
# use css fonts for fontawesome
FONT_ICONS = True
