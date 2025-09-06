"""
kgops - End-to-End Knowledge Graph Builder for RAG & Sharing
"""

from setuptools import setup, find_packages
import os

# Read long description from README
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
try:
    with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    # Fallback to basic requirements if file doesn't exist
    requirements = [
        'networkx>=3.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'pydantic>=2.0.0',
        'click>=8.0.0',
        'rich>=13.0.0',
        'pyyaml>=6.0',
        'jsonschema>=4.0.0',
        'python-dotenv>=1.0.0',
        'typing-extensions>=4.5.0',
    ]

setup(
    name="kgops",
    version="0.1.1",
    description="KGOps - End-to-End Knowledge Graph Operations for RAG & Data Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="KGOps Team",
    author_email="sohamchaudhari2004@gmail.com",
    url="https://github.com/SohamChaudhari2004/kgops",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'kgops=kgops.cli.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="knowledge-graph rag nlp ai machine-learning graph-database",
    project_urls={
        "Bug Reports": "https://github.com/SohamChaudhari2004/kgops/issues",
        "Source": "https://github.com/SohamChaudhari2004/kgops",
        "Documentation": "https://github.com/SohamChaudhari2004/kgops",
    },
)
