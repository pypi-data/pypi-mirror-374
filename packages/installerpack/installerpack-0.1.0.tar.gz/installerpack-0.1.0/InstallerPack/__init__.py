"""
InstallerPack v0.1.0

InstallerPack is a Python module designed to simplify adding 'Installer' functionality to Python applications.
It provides functions that can be linked to button clicks, enabling cloud-based version updates and seamless
rebuilding with `pyinstaller`.

Uses OctaStore for version storage. Configure OctaStore using `setocta(...)`.
"""


from .installerpack import setocta, OctaConfig, init, update

__all__ = [
    "setocta",
    "OctaConfig",
    "init",
    "update"
]