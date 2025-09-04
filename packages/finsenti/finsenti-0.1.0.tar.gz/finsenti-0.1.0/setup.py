"""
Setup script for the finsenti package.
"""

from setuptools import setup, find_packages
import re
import pathlib

here = pathlib.Path(__file__).parent
init_text = (here / "finsenti" / "__init__.py").read_text()
# version = re.search(r"__version__ = '([^']+)'", init_text).group(1)
init_file = here / "finsenti" / "__init__.py"
if init_file.exists():
    init_text = init_file.read_text()
    version_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", init_text)
    if version_match:
        version = version_match.group(1)

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="finsenti",
    version=version,
    author="Vaibhav Jha",
    author_email="vaibhavjha100@gmail.com",
    description="A package for financial sentiment analysis using news articles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vaibhavjha100/Sentiment-Analysis",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "marketminer",
        "google-genai",
        "python-dotenv",
        "transformers",
        "torch",
        "hf_xet",
        "scipy",
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Financial and Insurance Industry",
    ],
)