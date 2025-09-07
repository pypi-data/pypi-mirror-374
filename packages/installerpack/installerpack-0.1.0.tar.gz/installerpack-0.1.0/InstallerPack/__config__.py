# __config__.py
from enum import Enum

class VersionStyle(str, Enum):
    SEMVER = "semver"
    SHORTSEMVER = "shortsemver"
    CALVER = "calver"
    SEQVER = "seqver"
    BUILDVER = "buildver"
    HYBRIDVER = "hybridver"
    PREVER = "prever"
    ZERVER = "zerover"

# Default version style for the installer. You can override this in your app.
version_style: VersionStyle = VersionStyle.SEMVER