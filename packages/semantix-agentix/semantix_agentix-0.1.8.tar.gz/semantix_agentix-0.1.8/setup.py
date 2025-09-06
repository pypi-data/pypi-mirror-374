from setuptools import find_packages, setup

setup(
    name="semantix_agentix",
    version="0.1.8",
    author="Artur Rodrigues",  # noqa: E501
    author_email="artur.rodrigues@semantix.ai",  # noqa: E501
    description="ML Flow interceptor for Semantix AI Governance",  # noqa: E501
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
      "mlflow>=3.3.1",
      "psycopg2-binary>=2.9.10"
    ],
)
 