from setuptools import setup, find_packages

setup(
    name="duckai",
    version="0.1.0",
    description="CLI for DuckDuckGo AI",
    author="DuckAI",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "duckai=cli.main:main",
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        # Minimal dependencies - using standard library
    ],
)
