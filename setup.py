from setuptools import setup, find_packages
import io
import os


install_requires = [
    "mailchimp3",
    "oauth2client",
    "gspread",
    "beautifulsoup4",
    "requests",
    "geopy",
    "pandas",
    "algoliasearch",
    "spacy",
]

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rasa-demo",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # supported python versions
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10.12",
    ],
    packages=find_packages(where="demo"),
    version="2.0",
    install_requires=install_requires,
    description="Rasa Demo Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rasa Technologies GmbH",
    author_email="hi@rasa.com",
    maintainer="Akela Drissner-Schmid",
    maintainer_email="akela@rasa.com",
    license="GNU General Public License v3.0",
    url="https://github.com/rasahq/rasa-demo",
    download_url="https://github.com/RasaHQ/rasa-demo/archive/main.zip",
    project_urls={
        "Bug Reports": "https://github.com/rasahq/rasa-demo/issues",
        "Source": "https://github.com/rasahq/rasa-demo",
    },
)
