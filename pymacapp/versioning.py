import configparser
import os
import sys
from .validators import validate_version

LOCK_FILE = os.path.join(os.path.dirname(__file__), "VERSION_LOCK.ini")


def _version_str_to_list(version:str) -> "list[int]":
    try:
        lst = [int(_) for _ in version.split(".")]
    except ValueError:
        raise RuntimeError(f"invalid version detected: {version=} (str to int conversion error)")
    else:
        return lst


class VersionLocker:

    def make_lock_file(self, version:str) -> bool:
        if not os.path.exists(LOCK_FILE):
            if validate_version(_version_str_to_list(version)):
                self.config["VERSION"] = {"__version__":version}
                v = self.config["VERSION"]
                # print(f"new version: {v}")
                with open(LOCK_FILE, "w") as configfile:
                    self.config.write(configfile)
                    return True
            else:
                raise RuntimeError(f"invalid version detected: {version=}")
        return False
    
    def _update_version(self, version:str):
        os.remove(LOCK_FILE)
        self.config["VERSION"] = {"__version__":version}
        with open(LOCK_FILE, "w") as configfile:
            self.config.write(configfile)
            return True

    def check_version(self, version:str) -> bool:
        """check a version before a build

        :param version: a period-delimited string of integers representing a build version ("1.2.4.10") that must begin and end in a non-negative integer
        :type version: str
        :raises RuntimeError: _description_
        :return: _description_
        :rtype: bool
        """
        with open(LOCK_FILE, "r") as configfile:
            self.config.read_file(configfile)
            last_version = self.config["VERSION"]["__version__"]
            cur_ver_list = _version_str_to_list(version)
            last_ver_list = _version_str_to_list(last_version)
            if not validate_version(cur_ver_list):
                raise RuntimeError(f"invalid version detected: {version=}")
            elif len(cur_ver_list) != len(last_ver_list):
                raise RuntimeError(f"invalid version detected: {version=} (length mismatch)")
            elif cur_ver_list == last_ver_list:
                print(RuntimeWarning(f"\n\n[WARNING] current version ({version}) == last-built version ({last_version})"))
                if not input("\nAre you sure you want to continue with the build (y)? : ") == "y":
                    sys.exit("\n\nBuild Aborted by User\n\n")
                else:
                    return True
            else:
                for index, item in enumerate(cur_ver_list):
                    if item > last_ver_list[index]:
                        return True
                    elif item == last_ver_list[index]:
                        pass
                    elif item < last_ver_list[index]:
                        print(RuntimeWarning(f"\n\n[WARNING] current version ({version}) < last-built version ({last_version})"))
                        if not input("\nAre you sure you want to continue with the build (y)? : ") == "y":
                            sys.exit("\n\nBuild Aborted by User\n\n")
                        else:
                            return True

    def __init__(self, version:str) -> None:
        self.config = configparser.ConfigParser()
        self.version = version
    
    def lock(self):
        if not self.make_lock_file(self.version):
            if self.check_version(self.version):
                self._update_version(self.version)
