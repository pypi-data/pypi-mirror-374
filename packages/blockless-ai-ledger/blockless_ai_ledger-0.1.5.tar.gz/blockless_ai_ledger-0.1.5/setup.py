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
            "pytest-asyncio>=0.18.0"
        ]

setup(
    name="blockless-ai-ledger",
    version="0.1.0",
    author="Nethara Labs", 
    author_email="contact@netharalabs.com",
    description="Distributed AI-validated ledger system - Blockless blockchain with AI consensus",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/netharalabs/blockless",
    project_urls={
        "Bug Tracker": "https://github.com/netharalabs/blockless/issues",
        "Documentation": "https://github.com/netharalabs/blockless",
        "Source": "https://github.com/netharalabs/blockless",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
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
        ]
    },
    entry_points={
        "console_scripts": [
            "blockless=ai_ledger.cli:main",
            "blockless-node=ai_ledger.network_node:main",
            "blockless-demo=ai_ledger.demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_ledger": [
            "genesis.json",
            "*.yaml",
            "*.yml",
            "static/*",
            "templates/*"
        ]
    },
    zip_safe=False,
    keywords="blockchain, ai, distributed-ledger, cryptocurrency, validation",
    platforms=["any"],
)