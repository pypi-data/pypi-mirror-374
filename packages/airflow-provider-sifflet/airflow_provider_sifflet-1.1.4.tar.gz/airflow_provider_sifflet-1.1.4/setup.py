"""Setup.py for the airflow-provider-sifflet package."""

import sifflet_provider
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


def do_setup():
    """Perform the package airflow-provider-sifflet setup."""
    setup(
        name="airflow-provider-sifflet",
        description="Provider package airflow-provider-sifflet for Apache Airflow",
        version=sifflet_provider.__version__,
        long_description=long_description,
        long_description_content_type="text/markdown",
        license="Apache License 2.0",
        packages=find_packages(include=["sifflet_provider", "sifflet_provider.*"]),
        install_requires=["sifflet-sdk>=0.4.1"],
        setup_requires=["setuptools", "wheel"],
        author="Sifflet",
        author_email="support@siffletdata.com",
        url="https://www.siffletdata.com/",
        classifiers=[
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Framework :: Apache Airflow",
            "Framework :: Apache Airflow :: Provider",
        ],
        python_requires="~=3.7",
        entry_points={
            "apache_airflow_provider": ["provider_info=sifflet_provider.get_provider_info:get_provider_info"]
        },
        extras_require={
            "dev": ["apache-airflow"],
        },
    )


if __name__ == "__main__":
    do_setup()
