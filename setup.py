from setuptools import setup, find_packages  # type: ignore

with open("README.md") as f:
    long_description = f.read()

setup(
    name="followthemoney",
    version="2.1.8",
    author="Organized Crime and Corruption Reporting Project",
    author_email="data@occrp.org",
    url="https://docs.alephdata.org/developers/followthemoney",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    namespace_packages=[],
    include_package_data=True,
    package_data={"": ["followthemoney/schema/*", "followthemoney/translations/*"]},
    zip_safe=False,
    install_requires=[
        "babel",
        "pyyaml",
        "banal >= 1.0.1, < 1.1.0",
        "click >= 7.0",
        "stringcase >= 1.2.0",
        "requests >= 2.21.0",
        "python-levenshtein >= 0.12.0",
        "normality >= 2.1.1",
        "sqlalchemy >= 1.2.0",
        "countrynames >= 1.7.0",
        "languagecodes >= 1.0.7",
        "phonenumbers >= 8.9.11",
        "python-stdnum >= 1.10",
        "urlnormalizer >= 1.2.0",
        "pantomime >= 0.4.0",
        "pytz >= 2020.1",
        "rdflib >=5.0.0, < 5.1.0",
        "networkx >=2.5, < 2.6",
        "openpyxl >= 3.0.5",
        "pymisp >= 2.4.126",
    ],
    extras_require={
        "dev": [
            "pip>=10.0.0",
            "bump2version",
            "wheel>=0.29.0",
            "twine",
            "flake8>=2.6.0",
            "nose",
            "transifex-client",
            "responses>=0.9.0",
            "coverage>=4.1",
            "recommonmark>=0.4.0",
        ]
    },
    test_suite="nose.collector",
    entry_points={
        "babel.extractors": {"ftmmodel = followthemoney.messages:extract_yaml"},
        "followthemoney.cli": {
            "aggregate = followthemoney.cli.aggregate:aggregate",
            "sieve = followthemoney.cli.sieve:sieve",
            "link = followthemoney.cli.dedupe:link",
            "mapping = followthemoney.cli.mapping:run_mapping",
            "csv = followthemoney.cli.exports:export_csv",
            "excel = followthemoney.cli.exports:export_excel",
            "rdf = followthemoney.cli.exports:export_rdf",
            "gexf = followthemoney.cli.exports:export_gexf",
            "cypher = followthemoney.cli.exports:export_cypher",
        },
        "console_scripts": [
            "ftmutil = followthemoney.cli.cli:cli",
            "ftm = followthemoney.cli.cli:cli",
            "followthemoney = followthemoney.cli.cli:cli",
        ],
    },
    tests_require=["coverage", "nose"],
)
