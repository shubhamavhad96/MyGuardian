"""Setup script for rag-guardrail package."""
from setuptools import setup, find_packages
from pathlib import Path

readme = Path(__file__).parent.parent / "README.md"
long_description = readme.read_text() if readme.exists() else ""

setup(
    name="rag-guardrail",
    version="0.1.0",
    description="Production-ready guardrail system for RAG applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MyGuardian Team",
    author_email="team@example.com",
    url="https://github.com/yourusername/MyGuardian",
    packages=find_packages(where="."),
    package_dir={"": "."},
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.6",
        "pydantic>=2.9.2",
        "python-dotenv>=1.0.1",
        "redis>=5.0.7",
        "rq>=1.16.2",
        "numpy>=2.1.3",
        "scikit-learn>=1.5.2",
        "rank-bm25>=0.2.2",
        "pyyaml>=6.0.2",
        "prometheus-client>=0.20.0",
        "opentelemetry-api>=1.27.0",
        "opentelemetry-sdk>=1.27.0",
        "opentelemetry-exporter-otlp>=1.27.0",
        "opentelemetry-instrumentation-fastapi>=0.48b0",
    ],
    extras_require={
        "semantic": ["sentence-transformers>=2.2.0", "torch>=2.0.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)

