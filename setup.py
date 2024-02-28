from setuptools import setup
from pathlib import Path


# Extract parent directory
here = Path(__file__).absolute().parent

# Get the long description from README.md
with open(here.joinpath("README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION=f.read()

setup(
    name="telegrambot",
    version="0.1",
    author="ocriado91",
    description="Python package for interacting with Telegram Bot API",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=[
        "tomli",
        "requests",
        "wget"
    ],
    python_requires=">=3.6",
)