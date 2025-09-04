from setuptools import setup, find_packages

setup(
    name="cloudshell-cli",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "cloudshell-cli=cloudshell_cli.cli:cli",
        ],
    },
)
