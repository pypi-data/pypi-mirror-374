# protein_turnover_website

Website for protein turnover


## installation

```bash
pip install protein_turnover
pip install protein_turnover_website
# run the website (both frontend and back)
turnover web
```
Run just the website:

```bash
FLASK_APP=protein_turnover_website.wsgi flask run
# *OR*
gunicorn --workers=4 protein_turnover_website.wsgi
```

A posssibly superior entry point is to use [uv](https://docs.astral.sh/uv/). With `uv` installed you can install
`protein-turnover` (+plus website) with

```bash
uv tool install protein-turnover --with=protein-turnover-website --with=gunicorn
# ...
turnover web

# OR try it out with...

uv run --with=protein-turnover --with=protein-turnover-website --with=gunicorn turnover web

```

You can then just run `turnover web`.

You can even just try out the website ....

```bash
# OR just
uv run --with=protein-turnover-website --with=gunicorn turnover web -- --access-logfile=-
```

### Configure turnover website

You can run this as simple:

In the instance folder create a file `protein_turnover_website.cfg`

```python
MOUNTPOINTS = [
    ("/path/to/msms/files", "nickname"),
    # only show mzML file here
    ("/another/path/to/msms/files", "nickname", r".*\.mzML$")

]
```
Run the website with `turnover web` and
go the the `configuration.html` page for more information.
