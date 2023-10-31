from ..app import App
from ...logger import logger
from ...helpers import COLLECT_SCRIPTS_HERE
from ...command import Command
import time
import shutil
import os


class Package:
    def __init__(self, app: App, version: str = "0.0.1", identifier: str = None) -> None:
        self.app: App = app
        self.identifier = identifier
        self.version = version
        self.__build = None
        self.__dist = None
        self.__developer_id: str = None
        self.__developer_team_id: str = None
        self.__developer_app_specific_password: str = None
        logger.debug(f"{self} created")
        if not os.path.exists(self.app._app):
            logger.error(f"app build ('{self.app._app}') does not exist")
            raise RuntimeError()
        if not os.path.exists(COLLECT_SCRIPTS_HERE):
            try:
                os.mkdir(COLLECT_SCRIPTS_HERE)
            except:
                logger.warning(f"unable to make temp directory '{COLLECT_SCRIPTS_HERE}'")

    def __repr__(self) -> str:
        return f"Package({self.app=})"

    @property
    def is_logged_in(self):
        return self.__developer_id and self.__developer_app_specific_password and self.__developer_team_id

    def build(self, preinstall_script: str = None, postinstall_script: str = None,
              dist_path: str = os.path.join(os.getcwd(), "dist"), build_path: str = os.path.join(os.getcwd(), "build")):
        """build the current application into a {NAME}.pkg

        :param preinstall_script: location of a preinstall script, defaults to None
        :type preinstall_script: str, optional
        :param postinstall_script: location of a postinstall script, defaults to None
        :type postinstall_script: str, optional
        :param dist_path: where the built distributable should be placed once it is built, defaults to os.path.join(os.getcwd(), "dist-pkg")
        :type dist_path: str, optional
        :param build_path: where the distributable should be built, defaults to os.path.join(os.getcwd(), "build-pkg")
        :type build_path: str, optional
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
        if not os.path.exists(scripts):
            logger.debug(f"scripts directory '{scripts}' does not exist; attempting to create it now")
            os.mkdir(scripts)
        logger.debug(f"emptying '{scripts}'")
        [os.remove(os.path.join(scripts, _)) for _ in os.listdir(scripts)]
        verified_preinstall_script = None
        verified_postinstall_script = None
        if preinstall_script:
            if os.path.isfile(preinstall_script):
                if os.path.basename(preinstall_script) == "preinstall":
                    verified_preinstall_script = preinstall_script
                else:
                    logger.error(
                        f"the name of the preinstall script must be 'preinstall' exactly, without extension (currently {preinstall_script=})")
            else:
                logger.error(f"unable to verify '{preinstall_script=}'; it will be ignored")
        if postinstall_script:
            if os.path.isfile(postinstall_script):
                if os.path.basename(postinstall_script) == "postinstall":
                    verified_postinstall_script = postinstall_script
                else:
                    logger.error("the name of the postinstall script must be 'postinstall' exactly, without extension")
            else:
                logger.error(f"unable to verify '{postinstall_script=}'; it will be ignored")
        if verified_preinstall_script or verified_postinstall_script:
            if verified_preinstall_script:
                shutil.copyfile(verified_preinstall_script, os.path.join(scripts, "preinstall"))
            if verified_postinstall_script:
                shutil.copyfile(verified_postinstall_script, os.path.join(scripts, "postinstall"))
            logger.info(f"ensuring {scripts=} is executable (sudo chmod -R +x {scripts})")
            Command.run(f"sudo -S chmod -R +x {scripts}")

        # 2: productbuild
        build_command = f"pkgbuild"
        if self.version:
            build_command = build_command + f" --version {self.version}"
        if self.identifier:
            build_command = build_command + f" --identifier {self.identifier}"
        else:
            raise RuntimeError(f"cannot package without an identifier; set in the Package's constructor")
        if verified_preinstall_script or verified_postinstall_script:
            build_command = build_command + f" --scripts '{COLLECT_SCRIPTS_HERE}'"
        build_command = build_command + f" --root '{self.app._app}' --install-location '/Applications/{self.app._name}.app' '{os.path.join(self.__build, f'{self.app._name}.pkg')}'"
        Command.run(build_command)
        end = time.time()
        logger.info(f"(package) build completed in {round(end - start, 2)} second(s)")
        return self

    def sign(self, hash: str):
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
        Command.run(command)
        return self

    @staticmethod
    def get_first_hash(output: bool = False) -> str:
        """equivalent to running "security find-identity -p basic -v" in terminal and looking for the hash next to "Developer ID Installer"

        :param output: log output and errors from the command to find the application hash, defaults to False
        :type output: bool, optional
        :return: the Developer ID Installer hash
        :rtype: str
        """
        command = "security find-identity -p basic -v"
        process, output, error = Command.run(command, suppress_log=not output)
        if not error:
            lines = output.splitlines()
            for line in lines:
                if "Developer ID Installer" in str(line):
                    h = line.split()[1]
                    return h
        else:
            logger.debug(f"an error occurred: {error}")

    def login(self, apple_id: str, app_specific_password: str, team_id: str):
        """enter your login credentials

        :param apple_id: email of an Apple developer account, defaults to None
        :type apple_id: str, optional
        :param app_specific_password: app-specific password associated with an apple developer account, defaults to None
        :type app_specific_password: str, optional
        :param team_id: Apple Developer Team ID, found at https://developer.apple.com/account#MembershipDetailsCard
        :type team_id: str, optional
        """
        if apple_id is None:
            apple_id = input("apple developer id email (str): ")
        self.__developer_id = apple_id

        if app_specific_password is None:
            app_specific_password = input("app-specific password (str): ")
        self.__developer_app_specific_password = app_specific_password

        if team_id is None:
            team_id = input("apple developer team id (str): ")
        self.__developer_team_id = team_id

    def _check_login(self):
        if not self.is_logged_in:
            logger.warning(
                "pymacapp is not logged in to your Apple Developer account; call the .login(...) method first!")
            if input("Are you sure you want to continue (y): ") != "y":
                raise KeyboardInterrupt()

    def notarize(self, wait: bool = True):
        """notarize the current package through Apple's notary service (ensure you call .login(...) first)"""

        if not self.app._signed:
            logger.warning(
                f"pymacapp does not indicate that your app {self.app} was signed; notary service may fail if the .app is not signed (you should call .sign(...) on your App instance)")
            if input("Are you sure you want to continue (y): ") != "y":
                raise KeyboardInterrupt()

        self._check_login()

        command = f"""xcrun notarytool submit --apple-id={self.__developer_id} --password {self.__developer_app_specific_password} --team-id {self.__developer_team_id} '{os.path.join(self.__dist, f"{self.app._name}.pkg")}'"""
        if(wait):
            command = command + " --wait"

        logger.debug(f"signing with: {command}")
        logger.info("attempting to notarize")
        if(wait):
            logger.warn("waiting for notarization to complete, this may take some time; call .notarize(wait=False) if you do not want this behavior (NOT RECCOMENDED)")
        process = Command.run(command)
        output, error = process.output, process.error
        if output:
            for line in output.splitlines():
                if "  id:" in line:
                    self.__request_uuid = line.split(": ")[1]
                    logger.info(f"uploaded to notary service (uuid={self.__request_uuid})")
                    break
        return self

    def log_full_notary_log(self):
        """logs full notary output (called when notarization fails, used to get log from notary)"""
        self._check_login()
        command = f"xcrun notarytool log --apple-id={self.__developer_id} --password {self.__developer_app_specific_password} --team-id {self.__developer_team_id} {self.__request_uuid}"
        Command.run(command)

    def staple(self):
        """staple a package that has been notarized successfully, called automatically if .wait() is used after .notorize()"""
        logger.info("preparing to staple")
        package = os.path.join(self.__dist, f"{self.app._name}.pkg")
        command = f"xcrun stapler staple '{package}'"
        Command.run(command)
