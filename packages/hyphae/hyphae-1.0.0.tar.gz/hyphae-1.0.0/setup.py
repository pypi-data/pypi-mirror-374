from setuptools import setup, find_packages
from pathlib import Path
import os
HERE = Path(__file__).parent.resolve()
os.chdir(HERE)
setup(
    name="hyphae",
    version="1.0.0",
    description="The framework for developing TruffleOS agentic applications",
    author="Deepshard",
    author_email="accounts@deepshard.org",
    license="MIT",
    packages=find_packages(where=HERE, include=["hyphae*", "truffle*"]),
    package_dir={"": "."},
    install_requires=[
        "grpcio==1.72.0",
        "grpcio-reflection==1.72.0",
        "protobuf>=6.30.0",
        "requests>=2.32.3",
        "keyring>=25.6.0",
        "googleapis-common-protos"
    ],
    python_requires=">=3.10",
    setup_requires=["wheel"],
    entry_points={
        "console_scripts": [
            "hyphae=hyphae.cli:main",
        ],
    },      
)
