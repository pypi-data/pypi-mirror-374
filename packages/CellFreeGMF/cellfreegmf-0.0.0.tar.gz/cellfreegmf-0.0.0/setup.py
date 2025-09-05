import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# you need to change all these
VERSION = '0.0.0'
DESCRIPTION = 'cfRNA'
LONG_DESCRIPTION = 'Integrative Biomarker Discovery and Cell-of-Origin Tracing from Cell-Free Transcriptomes via Graph Matrix Factorization with Comparative Single-Cell Landscape Modeling in Health and Disease'

setup(
    name="CellFreeGMF",
    version=VERSION,
    author="Wenxiang Zhang",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'windows','mac','linux', 'cfRNA', 'CellFreeGMF'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
