from setuptools import find_packages, setup
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="semantix-agentix",
    version="0.1.8",
    author="Artur Rodrigues",  # noqa: E501
    author_email="artur.rodrigues@semantix.ai",  # noqa: E501
    description="A Python library for AI governance and experiment tracking that integrates with MLflow",  # noqa: E501
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "mlflow>=3.3.1",
        "psycopg2-binary>=2.9.10"
    ],
)
 