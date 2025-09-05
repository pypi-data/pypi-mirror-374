from setuptools import setup, find_packages

setup(
    name="bensgaming",  # Tên package trên PyPI
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "requests",
        "discord.py",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "bensgaming=bensgaming.main:main"
        ]
    },
    author="BensGaming",
    description="BensGamingOnTop.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7"
)
