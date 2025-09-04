from setuptools import setup, find_packages

setup(
    name="memory-cli",
    version="0.1.0",
    description="A CLI memory layer for developers across editors.",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "requests>=2.25.0",
        "nltk>=3.6.0"
    ],
    entry_points={
        "console_scripts": [
            "memory=memory_cli.cli:app",
        ],
    },
    python_requires=">=3.7",
) 