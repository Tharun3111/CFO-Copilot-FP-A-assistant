"""Setup configuration for fpa_copilot package."""
from setuptools import setup, find_packages

setup(
    name="fpa_copilot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.38.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "matplotlib>=3.8.0",
        "plotly>=5.22.0",
        "pytest>=8.0.0",
        "openpyxl>=3.1.0",
    ],
)