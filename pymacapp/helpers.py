import os


MINIMUM_ENTITLEMENTS = os.path.join(os.path.dirname(__file__), "entitlements.plist")
def write_minimum_entitlements() -> str:
    contents = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <!-- These are required for binaries built by PyInstaller -->
        <key>com.apple.security.cs.allow-jit</key>
        <true/>
        <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
        <true/>
        <key>com.apple.security.cs.disable-library-validation</key>
        <true/>
</dict>
</plist>"""
    try:
        with open(MINIMUM_ENTITLEMENTS,"w") as file:
            file.writelines(contents)
    except:
        raise RuntimeError("unable to create minimum entitlements file")
    return MINIMUM_ENTITLEMENTS

# All scripts should be copied into this folder
COLLECT_SCRIPTS_HERE = os.path.join(os.path.dirname(__file__), "Scripts/")

# pyinstaller constants
APP_NAME_REGEX = r"^[0-9A-Za-z\d\s]+$"
BUNDLE_IDENTIFIER_REGEX = r"^[A-Za-z0-9\.\-]+$"
ARCHITECTURES = ["x86_64", "arm64", "universal2"]
PYINSTALLER_LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]