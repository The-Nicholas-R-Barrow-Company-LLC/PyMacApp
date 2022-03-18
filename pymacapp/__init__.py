from .logger import logger
import subprocess, os, time, shutil
from .helpers import make_spec, MINIMUM_ENTITLEMENTS, DEFAULT_SCRIPTS, get_first_installer_hash

class Package:
    def __init__(self, app, version:str="0.0.1", identifier:str=None) -> None:
        self.app:App = app
        self.identifier = identifier
        self.version = version
        self.__build = None
        self.__dist = None
        logger.debug(f"{self} created")
        logger.debug(self.app._app)
    
    def __repr__(self) -> str:
        return f"Package({self.app=})"
    
    def build(self, output:str="installer.pkg", preinstall_script:str=None, postinstall_script:str=None, dist_path:str=os.path.join(os.getcwd(), "dist-pkg"), build_path:str=os.path.join(os.getcwd(), "build-pkg"), app_path:str=None):
        logger.debug(type(output))
        start = time.time()
        logger.info(f"(pkg) build initiated")
        self.__build = build_path
        if not os.path.exists(self.__build):
            logger.warning(f"{build_path=} does not exist; attempting to create")
            try:
                os.mkdir(self.__build)
            except:
                logger.error(f"unable to create {self.__build}")
            else:
                logger.info(f"created {self.__build}")
        self.__dist = dist_path
        if not os.path.exists(self.__dist):
            logger.warning(f"{dist_path=} does not exist")
            try:
                os.mkdir(self.__dist)
            except:
                logger.error(f"unable to create {self.__dist}")
            else:
                logger.info(f"created {self.__dist}")
        if app_path:
            if self.app._app:
                logger.warning(f"{self.app}.__app is not empty ({self.app._app}) but {app_path=} provided; using {app_path}")
            self.app._app = app_path
        if not self.app._app and not os.path.exists(self.app._app):
            logger.error(f"current app path ({self.app._app}) does not exist and {app_path=} does not exist; must set one")

        # 1: make sure Scripts are executable: sudo chmod -R +x $SCRIPTS
        scripts = DEFAULT_SCRIPTS
        PRE = None
        POST = None
        if preinstall_script:
            if os.path.isfile(preinstall_script):
                if os.path.basename(preinstall_script) == "preinstall":
                    PRE = preinstall_script
                else:
                    logger.error(f"the name of the preinstall script must be 'preinstall' exactly, without extension (currently {preinstall_script=})")
            else:
                logger.error(f"unable to verify '{preinstall_script=}'; it will be ignored")
        if postinstall_script:
            if os.path.isfile(postinstall_script):
                if os.path.basename(postinstall_script) == "postinstall":
                    POST = postinstall_script
                else:
                    logger.error("the name of the postinstall script must be 'postinstall' exactly, without extension")
            else:
                logger.error(f"unable to verify '{postinstall_script=}'; it will be ignored")
        if PRE or POST:
            for file in [f for f in os.listdir(DEFAULT_SCRIPTS) if os.path.isfile(os.path.join(DEFAULT_SCRIPTS, f))]:
                if file != "preinstall" and file != "postinstall":
                    logger.warning(f"found unknown file '{file}' in Scripts build directory ({DEFAULT_SCRIPTS}); it will be removed")
                    os.remove(os.path.join(DEFAULT_SCRIPTS, file))
            if PRE:
                # this is to preserve the default script
                if PRE != os.path.join(os.path.dirname(__file__), "Scripts", "preinstall"):
                    shutil.copyfile(PRE, os.path.join(os.path.dirname(__file__), "Scripts", "preinstall"))
            if POST:
                # this is to preserve the default script
                if POST != os.path.join(os.path.dirname(__file__), "Scripts", "postinstall"):
                    shutil.copyfile(POST, os.path.join(os.path.dirname(__file__), "Scripts", "postinstall"))
            logger.info(f"ensuring {scripts=} is executable (sudo chmod -R +x {scripts})")
            scripts_command = ["sudo", "chmod", "-R", "+x", scripts]
            try:
                process = subprocess.Popen(scripts_command, stdout=subprocess.PIPE, cwd=os.getcwd())
                output, error = process.communicate()
                if error:
                    logger.warning(error)
            except:
                logger.warning(f"unable to verify all scripts in '{scripts}' are executable")
        
        # 2: productbuild
        build_command = ["pkgbuild", "--root", self.app._app, "--install-location", f"/Applications/{self.app._name}.app", os.path.join(self.__build, f"{self.app._name}.pkg")]
        if PRE or POST:
            build_command.insert(1, DEFAULT_SCRIPTS)
            build_command.insert(1, "--scripts")
        if self.identifier:
            build_command.insert(1, self.identifier)
            build_command.insert(1, "--identifier")
        if self.version:
            build_command.insert(1, self.version)
            build_command.insert(1, "--version")
        if True:
            build_command.insert(1, get_first_installer_hash())
            build_command.insert(1, "--sign")
        debug_command = ' '.join(build_command)
        logger.debug(f"attempting pkgbuild command ({debug_command})")
        try:
            process = subprocess.Popen(build_command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
            if error:
                logger.warning(error)
        except:
            logger.error(f"unable to execute pkgbuild")
        # pkgbuild --identifier $PKG_IDENTIFIER \
        #  --sign "7C143CC5C54676696AFAA900D3DE34C07BC5C55F" \
        #  --version $APP_VERSION \
        #  --root "$APP_PATH" \
        #  --scripts "$SCRIPTS" \
        #  --install-location /Applications/"$APP_NAME".app "$TMP_PKG_PATH"
        return self

    def sign(self, hash:str):
        command = ["productsign", "--sign", hash, os.path.join(self.__build, f"{self.app._name}.pkg"), os.path.join(self.__dist, f"{self.app._name}.pkg")]
        logger.info("attempting to package sign")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
            if error:
                logger.warning(error)
        except:
            logger.error(f"unable to execute productsign")
        return self
    
    def notorize(self):
        return self

    def wait(self):
        return self
    
    def staple(self):
        return self
    
    def all(self) -> None:
        return None

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
        command = ["codesign", "--deep", "--force", "--timestamp", "--options", "runtime", "--entitlements", __entitlements, "--sign", __HASH, APP]
        if entitlements == None:
            logger.info(f"{entitlements=}, using default entitlements ({MINIMUM_ENTITLEMENTS=})")
            __entitlements = MINIMUM_ENTITLEMENTS
        elif os.path.exists(entitlements):
            __entitlements = entitlements
        else:
            logger.error(f"{entitlements=} does not exist")
        if not os.path.exists(APP):
            logger.error(f".app ('{APP}') does not exist")
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