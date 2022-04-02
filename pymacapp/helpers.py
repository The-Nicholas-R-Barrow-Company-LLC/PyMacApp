import os

MINIMUM_ENTITLEMENTS = os.path.join(os.path.dirname(__file__), "entitlements.plist")

# All scripts should be copied into this folder
COLLECT_SCRIPTS_HERE = os.path.join(os.path.dirname(__file__), "Scripts/")

# pyinstaller constants
APP_NAME_REGEX = r"^[0-9A-Za-z\d\s]+$"
BUNDLE_IDENTIFIER_REGEX = r"^[A-Za-z0-9\.\-]+$"
ARCHITECTURES = ["x86_64", "arm64", "universal2"]
PYINSTALLER_LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]