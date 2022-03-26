from .app_factory import App
from .logger import logger
from .helpers import COLLECT_SCRIPTS_HERE, cmd
import os, time, shutil, subprocess


class Package:
    def __init__(self, app, version:str="0.0.1", identifier:str=None) -> None:
        self.app:App = app
        self.identifier = identifier
        self.version = version
        self.__build = None
        self.__dist = None
        logger.debug(f"{self} created")
        if not os.path.exists(self.app._app):
            logger.error(f"app build ('{self.app._app}') does not exist")
            raise RuntimeError()
        if not os.path.exists(COLLECT_SCRIPTS_HERE):
            try:
                os.mkdir(COLLECT_SCRIPTS_HERE)
            except:
                logger.warning(f"unable to make directory '{COLLECT_SCRIPTS_HERE}'")
    
    def __repr__(self) -> str:
        return f"Package({self.app=})"
    
    # TODO: remove app_path or document it
    def build(self, preinstall_script:str=None, postinstall_script:str=None, dist_path:str=os.path.join(os.getcwd(), "dist"), build_path:str=os.path.join(os.getcwd(), "build")):
        """build the current application into a {NAME}.pkg

        :param preinstall_script: location of a preinstall script, defaults to None
        :type preinstall_script: str, optional
        :param postinstall_script: location of a postinstall script, defaults to None
        :type postinstall_script: str, optional
        :param dist_path: where the built distributable should be placed once it is built, defaults to os.path.join(os.getcwd(), "dist-pkg")
        :type dist_path: str, optional
        :param build_path: where the distributable should be built, defaults to os.path.join(os.getcwd(), "build-pkg")
        :type build_path: str, optional
        :param app_path: _description_, defaults to None
        :type app_path: str, optional
        :return: self (current package)
        :rtype: Package
        """
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

        # 1: make sure Scripts are executable: sudo chmod -R +x $SCRIPTS
        scripts = COLLECT_SCRIPTS_HERE
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
            for file in [f for f in os.listdir(COLLECT_SCRIPTS_HERE) if os.path.isfile(os.path.join(COLLECT_SCRIPTS_HERE, f))]:
                if file != "preinstall" and file != "postinstall":
                    logger.warning(f"found unknown file '{file}' in Scripts build directory ({COLLECT_SCRIPTS_HERE}); it will be removed")
                    os.remove(os.path.join(COLLECT_SCRIPTS_HERE, file))
            if PRE:
                # this is to preserve the default script
                if PRE != os.path.join(os.path.dirname(__file__), "Scripts", "preinstall"):
                    shutil.copyfile(PRE, os.path.join(os.path.dirname(__file__), "Scripts", "preinstall"))
            if POST:
                # this is to preserve the default script
                if POST != os.path.join(os.path.dirname(__file__), "Scripts", "postinstall"):
                    shutil.copyfile(POST, os.path.join(os.path.dirname(__file__), "Scripts", "postinstall"))
            logger.info(f"ensuring {scripts=} is executable (sudo chmod -R +x {scripts})")
            cmd(f"sudo chmod -R +x {scripts}")
        
        # 2: productbuild
        build_command = f"pkgbuild"
        if self.version:
            build_command = build_command + f" --version {self.version}"
        if self.identifier:
            build_command = build_command + f" --identifier {self.identifier}"
        if PRE or POST:
            build_command = build_command + f" --scripts '{COLLECT_SCRIPTS_HERE}'"
        build_command = build_command + f" --root '{self.app._app}' --install-location '/Applications/{self.app._name}.app' '{os.path.join(self.__build, f'{self.app._name}.pkg')}'"
        cmd(build_command)
        return self

    def sign(self, hash:str):
        """sign the current package

        :param hash: hash of an Installer ID (Developer); use pymacapp.helpers.get_first_installer_hash() to pull the default (see docs)
        :type hash: str
        :return: self (current package)
        :rtype: Package
        """
        command = f"productsign --sign {hash}" 
        command = command + f""" '{os.path.join(self.__build, f"{self.app._name}.pkg")}'"""
        command = command + f""" '{os.path.join(self.__dist, f"{self.app._name}.pkg")}'"""
        logger.debug(f"signing with: {command}")
        logger.info("attempting to package sign")
        cmd(command)
        return self
    
    def login(self, apple_id:str=None, app_specific_password:str=None):
        """helper function used by .notorize(...), .wait(...), and .staple(...)

        :param apple_id: email of an apple developer account, defaults to None
        :type apple_id: str, optional
        :param app_specific_password: app-specific password associated with an apple developer account, defaults to None
        :type app_specific_password: str, optional
        """
        if not hasattr(self, "_apple_id"):
            if apple_id == None:
                apple_id = input("apple developer id email (str): ")
            self._apple_id = apple_id
        if not hasattr(self, "_app_specific_password"):
            if app_specific_password == None:
                app_specific_password = input("app-specific password (str): ")
            self._app_specific_password = app_specific_password
    
    def notorize(self, apple_id:str=None, app_specific_password:str=None):
        """notorize the current package through Apple's notary service (requires .wait(...) or .staple(...), .wait(...) is reccomended)

        :param apple_id: email of an apple developer account, defaults to None
        :type apple_id: str, optional
        :param app_specific_password: app-specific password associated with an apple developer account, defaults to None
        :type app_specific_password: str, optional
        :return: self (current package)
        :rtype: Package
        """
        if not self.app._signed:
            logger.warning(f"pymacapp does not indicate that your app {self.app} was signed; notary service may fail if the .app is not signed (you should call .sign(...) on your App instance)")
            if input("Are you sure you want to continue (y): ") != "y":
                raise KeyboardInterrupt()
        self.login(apple_id=apple_id, app_specific_password=app_specific_password)
        command = f"""xcrun altool --notarize-app --primary-bundle-id {self.identifier} --username={apple_id} --password {app_specific_password} --file '{os.path.join(self.__dist, f"{self.app._name}.pkg")}'"""
        logger.debug(f"signing with: {command}")
        logger.info("attempting to notorize")
        process = cmd(command)
        output, error = process.output, process.error
        if output:
            for line in output.splitlines():
                if "RequestUUID" in line:
                    self._request_uuid = line.split(" = ")[1]
                    logger.info(f"uploaded to notary service (uuid={self._request_uuid})")
    # check status: xcrun altool --notarization-history 0 -u "nrb@nicholasrbarrow.com" -p "@keychain:Developer-altool"
    # if it fails: xcrun altool --username "nrb@nicholasrbarrow.com" --password "@keychain:Developer-altool" --notarization-info "Your-Request-UUID"
# when approved, run: xcrun stapler staple /Users/nicholasbarrow/GitHub/italian-department-budget-checker/Packages/build/Italian\ Department\ Budget\ Checker\ SIGNED.pkg
        return self

    def wait(self, apple_id:str=None, app_specific_password:str=None):
        """wait for a response from Apple's notary service and then handle response

        :param apple_id: email of an apple developer account, defaults to None
        :type apple_id: str, optional
        :param app_specific_password: app-specific password associated with an apple developer account, defaults to None
        :type app_specific_password: str, optional
        """
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
                                logger.info(f"waiting 10 seconds and then pulling debug log")
                                time.sleep(10)
                                self.log_full_notary_log()
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
    
    def log_full_notary_log(self, apple_id:str=None, app_specific_password:str=None):
        """logs full notary output (called when notarization fails, used to get log from notary)

        :param apple_id: email of an apple developer account, defaults to None
        :type apple_id: str, optional
        :param app_specific_password: app-specific password associated with an apple developer account, defaults to None
        :type app_specific_password: str, optional
        """
        self.login(apple_id=apple_id, app_specific_password=app_specific_password)
        command = ["xcrun", "altool", "--username", self._apple_id, "--password", self._app_specific_password, "--notarization-info", self._request_uuid]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        output, error = process.communicate()
        if output:
            out = output.decode("utf-8")
            for line in out.splitlines():
                logger.info(line)
        if error:
            out = output.decode("utf-8")
            for err in out.splitlines():
                logger.error(err)

    def staple(self):
        """staple a package that has been notorized successfully, called automatically if .wait() is used after .notorize()
        """
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