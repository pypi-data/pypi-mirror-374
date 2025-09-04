from __future__ import annotations

from .app import create_app

# entrypoint for say gunicorn or flask e.g.
# export FLASK_APP=protein_turnover_website.wsgi
# flask run
# *OR*
# gunicorn protein_turnover_website.wsgi
application = create_app()

del create_app
