from setuptools import setup

setup(
    name="odsc_default_sphinx_theme",
    version="0.1.1",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    packages=["odsc_default_sphinx_theme"],
    url="https://github.com/OpenDataServices/odsc_default_sphinx_theme",
    description="",
    install_requires=["furo"],
    extras_require={},
    entry_points={
        'sphinx.html_themes': [
            'odsc_default_sphinx_theme = odsc_default_sphinx_theme',
        ],
    },
    package_data={'odsc_default_sphinx_theme': ['static/*','theme.toml']},
)
