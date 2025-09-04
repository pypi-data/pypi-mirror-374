from os import path

def setup(app):
    app.add_html_theme('odsc_default_sphinx_theme', path.abspath(path.dirname(__file__)))

