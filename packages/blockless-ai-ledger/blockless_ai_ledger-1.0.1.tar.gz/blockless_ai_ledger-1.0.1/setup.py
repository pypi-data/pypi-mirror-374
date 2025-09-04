"""Setup script for AI Ledger - publish to PyPI for easy installation."""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "AI Ledger - Distributed AI-validated ledger system"

# Read requirements
# Read version from package
def read_version():
    try:
        with open("ai_ledger/__init__.py", "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split('"')[1]
    except FileNotFoundError:
        pass
    return "1.0.0"

def read_requirements():
    try:
        with open("requirements.txt", "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "fastapi>=0.68.0",
            "uvicorn[standard]>=0.15.0", 
            "pydantic>=1.8.0",
            "typer>=0.4.0",
            "aiohttp>=3.8.0",
            "cryptography>=3.4.8",
            "openai>=1.0.0",
            "colorama>=0.4.4",
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "PyNaCl>=1.5.0",
            "portalocker>=2.7.0",
            "psutil>=5.9.0",
            "loguru>=0.7.0"
        ]

setup(
    name="blockless-ai-ledger",
    version=read_version(),
    author="Nethara Labs", 
    author_email="contact@netharalabs.com",
    description="🌍 Global AI-powered blockchain - Join the worldwide decentralized network instantly",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/netharalabs/blockless",
    project_urls={
        "Bug Tracker": "https://github.com/netharalabs/blockless/issues",
        "Documentation": "https://github.com/netharalabs/blockless",
        "Source": "https://github.com/netharalabs/blockless",
        "Global Network": "https://ailedger.network",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence", 
        "Topic :: System :: Distributed Computing",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=22.0.0",
            "ruff>=0.0.290",
            "mypy>=0.991",
            "pytest-cov>=4.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.14.0",
            "grafana-client>=3.5.0",
        ],
        "production": [
            "docker>=6.0.0",
            "gunicorn>=20.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ailedger=ai_ledger.cli:main",
            "ailedger-node=ai_ledger.network_node:main",
            "ailedger-demo=ai_ledger.demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_ledger": [
            "genesis.json",
            "*.yaml",
            "*.yml",
            "static/*",
            "templates/*",
            "scripts/*"
        ]
    },
    zip_safe=False,
    keywords="blockchain, ai, distributed-ledger, cryptocurrency, validation, decentralized, global, consensus",
    platforms=["any"],
)