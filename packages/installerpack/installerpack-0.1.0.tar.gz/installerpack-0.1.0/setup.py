from setuptools import setup, find_packages

setup(
    name="installerpack",
    version="0.1.0",
    author="Uniplex LLC (formerly Taireru LLC)",
    author_email="tairerullc@gmail.com",
    description="InstallerPack is a Python module designed to simplify adding 'Installer' functionality to Python applications. It provides a single function that can be linked to button clicks, enabling cloud-based version updates and seamless rebuilding with `pyinstaller`.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TaireruLLC/octastore",
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)
