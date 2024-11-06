from setuptools import setup, find_packages
from pathlib import Path


def load_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()

long_description = (Path(__file__).parent / "README.md").read_text()

required_core = load_requirements("requirements.txt")
required_datasci = load_requirements("requirements-datasci.txt")
required_aws = load_requirements("requirements-aws.txt")

# Do not add SMAC for now in "extra" as it can easily conflict with Yahpo config-space version
# Do not add benchmarks either as it contains lots of dependencies can cause conflicts
required_all = required_datasci + required_aws

setup(
    name="scripts_and_notebooks",
    version=1.0,
    description="Collects a number of scripts (mostly Python) and Jupyter notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthias Seeger",
    packages=find_packages(
        include=[
            "script_utils",
            "script_utils.*",
        ]
    ),
    extras_require={
        "datasci": required_datasci,
        "aws": required_aws,
        "all": required_all,
    },
    install_requires=required_core,
    include_package_data=True,
)
