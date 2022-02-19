class app():
    filename="app.py"
    contents="""import logging, os, sys

def main():
    logger.debug("in main")
    # begin writing your code below

def resource_path(relative_path):
    \"\"\"returns absolute path for source and binary

    :param relative_path: path relative to main file(?)
    :type relative_path: str
    :return: absolute path
    :rtype: str
    \"\"\"
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # make logger
    logger = logging.Logger(__name__)
    logger.setLevel(logging.DEBUG)
    # make formatter
    formatter = logging.Formatter("(%(asctime)s) %(name)s @ %(lineno)d [%(levelname)s]: %(message)s")
    # make stream handler
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    # file handler
    fileHandler = logging.FileHandler(resource_path("log.log"))
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    # done!
    logger.debug("pre-initialization complete")
    main()
"""

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