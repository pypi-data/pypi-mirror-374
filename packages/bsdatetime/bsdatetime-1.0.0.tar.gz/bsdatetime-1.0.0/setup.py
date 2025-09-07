from setuptools import setup, find_packages
from pathlib import Path

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="bsdatetime",
    version="1.1.0",
    packages=find_packages(include=["bsdatetime", "bsdatetime.*", "bikram_sambat", "bikram_sambat.*"]),
    include_package_data=True,
    install_requires=[
        # No dependencies - pure Python
    ],
    python_requires=">=3.9",
    description="Bikram Sambat (Nepali) date/datetime conversion and utilities",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Rajendra Katuwal",
    author_email="raj.katuwal2061@gmail.com",
    url="https://github.com/Rajendra-Katuwal/bsdatetime",
    project_urls={
        "Documentation": "https://Rajendra-Katuwal.github.io/bsdatetime.docs/",
        "Source": "https://github.com/Rajendra-Katuwal/bsdatetime",
        "Issues": "https://github.com/Rajendra-Katuwal/bsdatetime/issues",
    },
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=["bikram sambat", "nepali", "calendar", "date", "datetime", "conversion"],
)
