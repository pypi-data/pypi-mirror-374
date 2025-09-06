from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="terminal-karaoke",
    version="1.0.3",
    author="Dexter Morgan",
    author_email="paarivah@proton.me",
    description="A terminal-based karaoke player",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hissterical/terminal-karaoke",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    install_requires=[
        "beautifulsoup4>=4.13.5",
        "pygame>=2.6.1",
        "requests>=2.32.5",
        "windows-curses>=2.3.0; platform_system=='Windows'",
        "yt-dlp>=2025.8.27",
    ],
    entry_points={
        "console_scripts": [
            "terminal-karaoke=terminal_karaoke.main:run",
        ],
    },
)