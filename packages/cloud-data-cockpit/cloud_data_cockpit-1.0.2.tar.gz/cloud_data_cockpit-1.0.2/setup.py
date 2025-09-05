# setup.py

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cloud-data-cockpit",
    version="1.0.2",
    description="An interactive interface for selecting and partitioning data with Dataplug.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Usama Benabdelkrim Zakan",
    author_email="usama.benabdelkrim@urv.cat",
    url="https://github.com/ubenabdelkrim/data_cockpit",
    packages=find_packages(
        include=["cloud_data_cockpit", "cloud_data_cockpit.*"]
    ),
    include_package_data=True,
    package_data={
        "cloud_data_cockpit": [
            "data/*.json",
            "widgets/styles/*.css",
        ],
    },
    install_requires=[
        "boto3",
        "ipywidgets",
        "gql",
        "cloud-dataplug",
        "requests_toolbelt",
        "rasterio"
    ],
    extras_require={
        "geospatial": [
            "cloud-dataplug[geospatial]",
            "pdal"
        ],
        "metabolomics": [
            "cloud-dataplug[metabolomics]"
        ]
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
