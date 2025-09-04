"""Setup script for TPS Agent library."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tps-agent",
    version="2.2.0",
    author="Earlypay",
    author_email="dev@earlypay.co.kr",
    description="Comprehensive TPS monitoring and throttling library with database-driven controls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tps-agent/tps-agent",
    packages=find_packages(include=["tps_agent", "tps_agent.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Database",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0,<3.0.0",
    ],
    extras_require={
        "postgresql": [
            "psycopg2-binary>=2.9.0,<3.0.0",
        ],
        "prometheus": [
            "prometheus_client>=0.16.0,<1.0.0",
        ],
        "all": [
            "psycopg2-binary>=2.9.0,<3.0.0",
            "prometheus_client>=0.16.0,<1.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "psycopg2-binary>=2.9.0,<3.0.0",
            "prometheus_client>=0.16.0,<1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tps-agent-test=tps_agent.cli:main",
        ],
    },
)
