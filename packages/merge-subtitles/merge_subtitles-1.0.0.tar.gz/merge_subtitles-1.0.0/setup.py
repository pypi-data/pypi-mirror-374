#!/usr/bin/env python3

from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements if they exist
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

setup(
    name="merge-subtitles",
    version="1.0.0",
    author="Lorenzo Wood",
    author_email="lorenzo@lorenzowood.com",
    description="A tool for merging MP4 video files with SRT subtitle files into MKV format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lorenzowood/merge-subtitles",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "merge-subtitles=merge_subtitles.main:main",
        ],
    },
    keywords="video subtitles ffmpeg mp4 srt mkv conversion",
    project_urls={
        "Bug Reports": "https://github.com/lorenzowood/merge-subtitles/issues",
        "Source": "https://github.com/lorenzowood/merge-subtitles",
    },
)