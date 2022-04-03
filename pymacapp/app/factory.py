import os
import time
from ..pyinstaller import spec
from ..helpers import MINIMUM_ENTITLEMENTS, write_minimum_entitlements
from ..command import Command
from ..logger import logger


class App:
    def __init__(self, name: str, identifier: str = None, icon: str = None) -> None:
        """create a new application instance

        :param name: the name of your application (i.e. "My New App")
        :type name: str
        :param identifier: a string of letters and periods, indicating a unique identifier for this app, defaults to None
        :type identifier: str, optional
        :param icon: path to an icon file for your app
        :type icon: str, optional
        """
        self._name = name
        if self._name[-4:] == ".app":
            logger.info(
                f"{name=} should not end in .app; this will be removed automatically ({self._name} -> {self._name[:-4]})")
            self._name = self._name[:-4]
        self._identifier = identifier
        self._icon = None
        if icon:
            if not os.path.exists(icon) and not os.path.isfile(icon):
                logger.info(f"{icon} does not exist or is not a file; it will be ignored")
                self._icon = None
            else:
                self._icon = os.path.abspath(icon)
        self._main_script = None
        self._spec = None
        self._build = None
        self._dist = None
        self._app = None
        # check vars
        self._built = False
        self._signed = False
        # config()
        self._pyinstaller_log_level: str = None
        self._entitlements: str = None
        logger.debug(f"{self} created")

    def __repr__(self) -> str:
        return f"App({self._name=})"

    def config(self, main: str, architecture: str = "universal2", entitlements: str = MINIMUM_ENTITLEMENTS,
               specpath: str = os.path.abspath(os.path.dirname(__file__)), log_level: str = "WARN",
               brute: bool = False):
        """configure the .spec file that pyinstaller uses to build the app

        :param main: the main script (main.py, etc.) where you run your application from
        :type main: str
        :param architecture: the arhitecture to build your app for, defaults to "universal2"
        :type architecture: str, optional
        :param entitlements: an entitlements file, defaults to MINIMUM_ENTITLEMENTS
        :type entitlements: str, optional
        :param specpath: the directory to store the .spec file in, defaults to os.path.abspath(os.path.dirname(__file__))
        :type specpath: str, optional
        :param log_level: the level of output to be displayed from pyinstaller, defaults to "WARN"
        :type log_level: str, optional
        :param brute: override built-in checks by pymacapp, defaults to False
        :type brute: bool, optional
        :return: self (current app)
        :rtype: App
        """
        if not os.path.exists(MINIMUM_ENTITLEMENTS):
            write_minimum_entitlements()
        self._spec = spec(name=self._name,
                          main_script=main,
                          icon=self._icon,
                          identifier=self._identifier,
                          architecture=architecture,
                          entitlements=entitlements,
                          specpath=specpath,
                          log_level=log_level,
                          brute=False)
        self._pyinstaller_log_level: str = log_level
        self._entitlements = entitlements
        return self

    def build(self, dist_path: str = os.path.join(os.getcwd(), "dist"),
              build_path: str = os.path.join(os.getcwd(), "build")):
        """build the current application into a {NAME}.app

        :param dist_path: where the built distributable should be placed once it is built, defaults to os.path.join(os.getcwd(), "dist")
        :type dist_path: str, optional
        :param build_path: where the distributable should be built, defaults to os.path.join(os.getcwd(), "build")
        :type build_path: str, optional
        :return: self (current app)
        :rtype: App
        """
        start = time.time()
        logger.info(f"(app) build initiated")
        self._build = build_path
        self._dist = dist_path
        self._app = os.path.join(self._dist, f"{self._name}.app")
        if not self._spec:
            logger.error(f"'{self}.__spec' is currently None; call {self}.config(...) to set this value")
            raise RuntimeError(f"'{self}.__spec' is currently None; call {self}.config(...) to set this value")
        if not os.path.isdir(self._dist):
            logger.warning(f"dist_path ('{self._dist}') does not exist; attempting to create")
            try:
                os.mkdir(self._dist)
            except:
                raise RuntimeError(f"failed to create non-existent dist_path ('{self._dist}')")
        if not os.path.isdir(self._build):
            logger.warning(f"build_path ('{self._build}') does not exist; attempting to create")
            try:
                os.mkdir(self._build)
            except:
                raise RuntimeError(f"failed to create non-existent build_path ('{self._build}')")

        command = f"pyinstaller --noconfirm --log-level {self._pyinstaller_log_level} --distpath '{self._dist}' --workpath '{self._build}' '{self._spec}'"
        Command.run(command)
        self._built = True
        end = time.time()
        logger.info(f"(app) build completed in {round(end - start, 2)} second(s)")
        return self

    def sign(self, hash: str):
        """sign an application

        :param hash: hash of an Application ID (Developer); use pymacapp.helpers.get_first_application_hash() to pull the default (see docs)
        :type hash: str
        :return: self (current app)
        :rtype: App
        """
        APP = self._app
        __entitlements = ""
        __HASH = hash
        if self._entitlements == None:
            logger.info(f"{self._entitlements=}, using default entitlements ({MINIMUM_ENTITLEMENTS=})")
            if not os.path.exists(MINIMUM_ENTITLEMENTS):
                write_minimum_entitlements()
            __entitlements = MINIMUM_ENTITLEMENTS
        elif os.path.exists(self._entitlements):
            __entitlements = self._entitlements
        else:
            logger.error(f"{self._entitlements=} does not exist")
        if not os.path.exists(APP):
            logger.error(f".app ('{APP}') does not exist; call .build(...) first")
        command = f"codesign --deep --force --timestamp --options runtime --entitlements '{__entitlements}' --sign '{__HASH}' '{APP}'"
        Command.run(command)
        self._signed = True
        return self

    def verify(self):
        """verify the signature on the app by sending output to console, optional / not required (for debug purposes only)

        :return: self (current app)
        :rtype: App
        """
        logger.info("***** begin signature verification *****")
        Command.run(f"codesign --verify --verbose '{self._app}'")
        Command.run(f"codesign -dvvv '{self._app}'")
        logger.info("***** end signature verification *****")
        return self

    @staticmethod
    def get_first_hash(output: bool = False) -> str:
        """equivalent to running "security find-identity -p basic -v" in terminal and looking for the hash next to "Developer ID Application"

        :param output: log output and errors from the command to find the application hash, defaults to False
        :type output: bool, optional
        :return: the Developer ID Application hash
        :rtype: str
        """
        command = "security find-identity -p basic -v"

        # process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        process, output, error = Command.run(command, suppress_log=not output)
        if not error:
            lines = output.splitlines()
            for line in lines:
                if "Developer ID Application" in str(line):
                    h = line.split()[1]
                    return h
        else:
            logger.debug(f"an error occurred: {error}")

