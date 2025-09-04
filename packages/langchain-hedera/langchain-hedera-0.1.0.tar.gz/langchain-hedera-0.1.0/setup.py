"""
Setup script for langchain-hedera package
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from pyproject.toml
version = "0.1.0"

setup(
    name="langchain-hedera",
    version=version,
    author="Sam Savage",
    author_email="admin@quantdefi.ai",
    description="LangChain integration for Hedera DeFi analytics with intelligent agents and tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samthedataman/langchain-hedera",
    project_urls={
        "Bug Tracker": "https://github.com/samthedataman/langchain-hedera/issues",
        "Repository": "https://github.com/samthedataman/langchain-hedera",
        "Documentation": "https://langchain-hedera.readthedocs.io",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-core>=0.1.0", 
        "langchain-community>=0.0.10",
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "python-dateutil>=2.8.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0", 
            "flake8>=4.0.0",
            "mypy>=0.950",
            "jupyter>=1.0.0",
            "langchain-openai>=0.0.5",
            "python-dotenv>=1.0.0",
        ],
        "examples": [
            "langchain-openai>=0.0.5",
            "jupyter>=1.0.0",
            "python-dotenv>=1.0.0", 
            "streamlit>=1.28.0",
            "plotly>=5.0.0",
        ],
        "hedera": [
            "hedera-defi>=0.3.0",  # Our base Hedera SDK
        ]
    },
    keywords=[
        "langchain",
        "hedera", 
        "defi",
        "blockchain",
        "analytics",
        "agents",
        "llm",
        "cryptocurrency",
        "saucerswap",
        "bonzo-finance"
    ],
    include_package_data=True,
    package_data={
        "langchain_hedera": ["py.typed"],
    },
    zip_safe=False,
)