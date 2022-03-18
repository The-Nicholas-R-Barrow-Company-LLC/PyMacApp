import os, shutil
from ..logger import logger

class DefaultPreinstallScript:
    def __init__(self) -> None:
        self._filename="preinstall"
        self._contents="""#!/bin/bash
exit 0 ## if you do not exit 0, any non-0 exits will cause install to fail
# ****** WARNING ******
# This file is created by using the pymacapp.scripthelpers.DefaultPostinstallScript class.
# Changes made in this file directly will automatically be overridden.
# ****** WARNING ******"""
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "Scripts")):
            os.mkdir(os.path.join(os.path.dirname(__file__), "Scripts"))
        with open(os.path.join(os.path.dirname(__file__), "Scripts", self._filename), "w") as f:
            f.writelines(self._contents)
    def path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "Scripts", self._filename)

class DefaultPostinstallScript:
    def __init__(self, app_name) -> None:
        self._filename="postinstall"
        self._contents=f"""#!/bin/bash
APP="{app_name}.app"
sudo chmod -R a+rwx /Applications/$APP
# exit 0 ## if you do not exit 0, any non-0 exits will cause install to fail
# # ****** WARNING ******
# This file is created by using the pymacapp.scripthelpers.DefaultPostinstallScript class.
# Changes made in this file directly will automatically be overridden.
# ****** WARNING ******"""
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "Scripts")):
            os.mkdir(os.path.join(os.path.dirname(__file__), "Scripts"))
        with open(os.path.join(os.path.dirname(__file__), "Scripts", self._filename), "w") as f:
            f.writelines(self._contents)
    
    def path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "Scripts", self._filename)