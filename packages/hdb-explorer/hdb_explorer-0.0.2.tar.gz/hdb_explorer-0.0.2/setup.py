from setuptools import setup, find_packages
from pathlib import Path

current_dir = Path( __file__ ).parent
readme = (current_dir / "README.md" ).read_text()

setup(
    name="hdb_explorer",
    version="0.0.2",
    packages=find_packages() + ["common", "db", "ui"],
    package_dir={
        "common": "hdb_explorer/common",
        "db": "hdb_explorer/db",
        "ui": "hdb_explorer/ui"
    },
    install_requires=[
        "hdbcli>=2.24.24",
        "httpx>=0.27.2",
        "textual>=5.3.0",
        "textual-autocomplete>=4.0.5",
        "textual[syntax]",
        "typing-extensions>=4.12.2"
    ],
    author="Praveen Nair",
    author_email="",
    description="A simple SAP HANA Database Explorer.",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    project_urls={
        "Source Repository": "https://github.com/praveen-nair/hdb_explorer/",
        "Issues": "https://github.com/praveen-nair/hdb_explorer/issues"
    },
    entry_points={
        "console_scripts": [
            "hdb_explorer = hdb_explorer.__main__:main",  
        ],
    },
)