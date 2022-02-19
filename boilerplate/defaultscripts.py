class entitlements():
    filename="entitlements.plist"
    contents="""<?xml version="1.0" encoding="UTF-8"?>
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
        <!-- These are required for binaries built by PyInstaller -->
</dict>
</plist>
"""

class preinstall():
    filename="preinstall"
    contents="""#!/bin/bash
exit 0
"""
class postinstall():
    filename="postinstall"
    contents="""#!/bin/bash
APP_NAME="My New App"
sudo chmod -R a+rwx /Applications/"$APP_NAME".app
# exit 0
"""