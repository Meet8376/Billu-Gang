"""
Setup configuration for backend package
"""

from setuptools import setup, find_packages

setup(
    name="ae01-backend",
    version="0.1.0",
    description="Backend for AE-01 Unified Agentic Coding Harness",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "sqlalchemy>=2.0.25",
        "tree-sitter>=0.21.0",
        "GitPython>=3.1.41",
        "sentence-transformers>=2.3.1",
        "tiktoken>=0.5.2",
        "networkx>=3.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "black>=24.1.1",
            "ruff>=0.1.14",
            "mypy>=1.8.0",
        ]
    },
)
