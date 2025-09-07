from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="beatpy",
    version="0.0.2",
    author="Alejo Prieto Dávalos",
    packages=find_packages(),
    description="Análisis de audio.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/beatpy/",
    project_urls={
        "Source": "https://github.com/AlejoPrietoDavalos/beatpy/"
    },
    python_requires=">=3.11",
    install_requires=[
        "yt_dlp>=2025.1.26",
        "requests>=2.32.3",
        "fastapi>=0.115.8",
        "uvicorn>=0.34.0",
        "numpy>=2.1.3",
        "librosa>=0.11.0",
        "soundfile>=0.13.1",
        "matplotlib>=3.10.1",
        "python-dotenv>=1.1.0"
    ],
    include_package_data=True
)
