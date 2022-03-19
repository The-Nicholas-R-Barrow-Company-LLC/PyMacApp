from .logger import logger
import os, subprocess, time
from .helpers import make_spec, MINIMUM_ENTITLEMENTS

class App:
    def __init__(self, name:str, identifier:str=None) -> None:
        self._name = name
        if self._name[-4:] == ".app":
            logger.info(f"{name=} should not end in .app; this will be removed automatically ({self._name} -> {self._name[:-4]})")
            self._name = self._name[:-4]
        self._identifier = identifier
        self._main_script = None
        self._spec = None
        self._build = None
        self._dist = None
        self._app = None
        # check vars
        self._built = False
        self._signed = False
        logger.debug(f"{self} created")

    def __repr__(self) -> str:
        return f"App({self._name=})"

    def setup(self, script:str, overwrite=False):
        self._main_script = script
        if not os.path.exists(self._main_script):
            logger.error(f"{script=} does not exist")
        parent_path = os.path.abspath(os.path.dirname(self._main_script))
        file_path = os.path.join(parent_path, f"{self._name}.spec")
        if os.path.exists(file_path):
            logger.info(f"'{file_path}' exists (delete to re-generate or set overwrite=True)")
            self._spec = file_path
            if overwrite:
                logger.info(f"{overwrite=}, re-generating '{file_path}'")
                self._spec = make_spec(self._name, self._identifier, self._main_script, parent_path)
        else:
            logger.info(f"creating '{file_path}'")
            self._spec = make_spec(self._name, self._identifier, self._main_script, parent_path)
        return self
    
    def build(self, dist_path:str=os.path.join(os.getcwd(), "dist"), build_path:str=os.path.join(os.getcwd(), "build"), suppress_pyinstaller_output=True):
        start = time.time()
        logger.info(f"(app) build initiated")
        self._build = build_path
        self._dist = dist_path
        if not self._spec:
            logger.error(f"'{self}.__spec' is currently None; call {self}.spec() to set this value")
        else:
            command = ["pyinstaller", "--noconfirm", "--distpath", f'{self._dist}', "--workpath", f'{self._build}', self._spec]
            if suppress_pyinstaller_output:
                command.insert(2, "--log-level")
                command.insert(3, "WARN")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
            if error:
                logger.warning(error)
            else:
                end = time.time()
                logger.info(f"build completed in {round(end-start, 3)} seconds without errors detected")
        return self
    
    def sign(self, hash:str, entitlements:str=None):
        """sign an application

        :param hash: hash of an Application ID (Developer); use pymacapp.helpers.get_first_application_hash() to pull the default (see docs)
        :type hash: str
        :param entitlements: entitlements.plist file; use None for default/minimum file, defaults to None
        :type entitlements: str, optional
        :return: self (current app)
        :rtype: App
        """        
        APP = os.path.join(self._dist, f"{self._name}.app")
        self._app = APP
        __entitlements = ""
        __HASH = hash
        if entitlements == None:
            logger.info(f"{entitlements=}, using default entitlements ({MINIMUM_ENTITLEMENTS=})")
            __entitlements = MINIMUM_ENTITLEMENTS
        elif os.path.exists(entitlements):
            __entitlements = entitlements
        else:
            logger.error(f"{entitlements=} does not exist")
        if not os.path.exists(APP):
            logger.error(f".app ('{APP}') does not exist")
        command = ["codesign", "--deep", "--force", "--timestamp", "--options", "runtime", "--entitlements", __entitlements, "--sign", __HASH, APP]
        debug_command = ""
        for c in command:
            if " " in c:
                debug_command = f"{debug_command} '{c}'"
            else:
                debug_command = f"{debug_command} {c}"
        logger.debug(f"(app) signing with: {debug_command}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        output, error = process.communicate()
        if error:
            logger.warning(error)
        else:
            end = time.time()
            logger.info(f"sign completed")
        return self
    
    def verify(self):
        command = ["codesign", "--verify", "--verbose", self._app]
        command2 = ["codesign", "-dvvv", self._app]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        logger.info("***** begin signature verification *****")
        output, error = process.communicate()
        if error:
            logger.warning(error)
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, cwd=os.getcwd())
        output, error = process2.communicate()
        if error:
            logger.warning(error)
        logger.info("***** end signature verification *****")
        return self
        
    # def package(self, identifier:str) -> Package:
    #     app = self
    #     package:Package = Package(app, identifier)
    #     return package