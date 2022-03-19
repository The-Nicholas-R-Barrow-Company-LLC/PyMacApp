from .app_factory import App
from .logger import logger
from .helpers import DEFAULT_SCRIPTS
import os, time, shutil, subprocess


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
    
    def build(self, hash:str, preinstall_script:str=None, postinstall_script:str=None, dist_path:str=os.path.join(os.getcwd(), "dist-pkg"), build_path:str=os.path.join(os.getcwd(), "build-pkg"), app_path:str=None):
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
            build_command.insert(1, hash)
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
        return self

    def sign(self, hash:str):
        command = ["productsign", "--sign", hash, os.path.join(self.__build, f"{self.app._name}.pkg"), os.path.join(self.__dist, f"{self.app._name}.pkg")]
        debug_command = ""
        for c in command:
            if " " in c:
                debug_command = f"{debug_command} '{c}'"
            else:
                debug_command = f"{debug_command} {c}"
        logger.debug(f"signing with: {debug_command}")
        logger.info("attempting to package sign")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
            if error:
                logger.warning(error)
        except Exception as e:
            logger.error(f"unable to execute productsign: {e}")
        else:
            logger.info("sign command executed")
        return self
    
    def login(self, apple_id:str=None, app_specific_password:str=None):
        if not hasattr(self, "_apple_id"):
            if apple_id == None:
                apple_id = input("apple developer id email (str): ")
            self._apple_id = apple_id
        if not hasattr(self, "_app_specific_password"):
            if app_specific_password == None:
                app_specific_password = input("app-specific password (str): ")
            self._app_specific_password = app_specific_password
    
    def notorize(self, apple_id:str=None, app_specific_password:str=None):
        self.login(apple_id=apple_id, app_specific_password=app_specific_password)
        try:
            command = ["xcrun", "altool", "--notarize-app", "--primary-bundle-id", self.identifier, f"--username={apple_id}", "--password", f"{app_specific_password}", "--file", os.path.join(self.__dist, f"{self.app._name}.pkg")]
            logger.info("attempting to notorize")
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
                output, error = process.communicate()
                if output:
                    out = output.decode("utf-8")
                    for line in out.splitlines():
                        if "RequestUUID" in line:
                            self._request_uuid = line.split(" = ")[1]
                if error:
                    errs = error.decode("utf-8")
                    for err in errs.splitlines():
                        logger.error(err)
            except:
                logger.error(f"unable to notorize")
            else:
                logger.info("notorize command executed")
                try:
                    if self._request_uuid:
                        logger.info(f"uploaded to notary service (uuid={self._request_uuid})")
                except:
                    pass
        except AttributeError as e:
            logger.error(f"attribute error: {e}")
    # check status: xcrun altool --notarization-history 0 -u "nrb@nicholasrbarrow.com" -p "@keychain:Developer-altool"
    # if it fails: xcrun altool --username "nrb@nicholasrbarrow.com" --password "@keychain:Developer-altool" --notarization-info "Your-Request-UUID"
# when approved, run: xcrun stapler staple /Users/nicholasbarrow/GitHub/italian-department-budget-checker/Packages/build/Italian\ Department\ Budget\ Checker\ SIGNED.pkg
        return self

    def wait(self, apple_id:str=None, app_specific_password:str=None):
        self.login(apple_id=apple_id, app_specific_password=app_specific_password)
        try:
            if self._request_uuid:
                check_again = True
                while check_again:
                    # command = ["xcrun", "altool", "--notarization-history", "0", "-u", self._apple_id, "-p", self._app_specific_password]
                    command = ["xcrun", "altool", "--username", self._apple_id, "--password", self._app_specific_password, "--notarization-info", self._request_uuid]
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
                    output, error = process.communicate()
                    if output:
                        out = output.decode("utf-8")
                        for line in out.splitlines():
                            logger.info(line)
                            if "Status Message: Package Invalid" in line:
                                check_again = False
                                logger.error(f"unable to notorize (invalid package for uuid={self._request_uuid})")
                            elif "Status Message: Package Approved" in line:
                                check_again = False
                                logger.info("successful notorization; automatically attempting to staple")
                                self.staple()
                    if error:
                        errs = error.decode("utf-8")
                        for err in errs.splitlines():
                            logger.error(err)
                    time.sleep(5)
        except AttributeError:
            logger.error(f"self._request_uuid does not exist; call .notorize(...) first")
    
    def get_full_notary_log(self):
        pass
    
    def staple(self):
        logger.info("preparing to staple")
        command = ["xcrun", "stapler", "staple", os.path.join(self.__dist, f"{self.app._name}.pkg")]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        output, error = process.communicate()
        if output:
            out = output.decode("utf-8")
            for line in out.splitlines():
                logger.info(line)
        if error:
            errs = error.decode("utf-8")
            for err in errs.splitlines():
                logger.error(err)
        return self