from setuptools import setup, find_packages

setup(
    name="rocketsniff",
    version="1.1.0",  # bump version for update
    author="Your Name",
    description="Python module to find Rocket League server IP and port from logs",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "RocketSniff=rocketsniff.cli:main"
        ]
    },
)
