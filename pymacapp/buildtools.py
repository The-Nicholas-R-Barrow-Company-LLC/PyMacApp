import subprocess, os, logging, traceback, re, time
from .defaultscripts import entitlements as entitlements_file

logger = logging.Logger(__name__)
formatter = logging.Formatter("[BOILERPLATE] (%(asctime)s) %(name)s @ %(lineno)d [%(levelname)s]: %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
identifier_regex = "^[a-zA-Z0-9\-.]+$"
hash_regex = "^[A-Z0-9]*$"

def make_spec(app_name:str, app_bundle_identifier:str, main_python_file:str, spec_path:str) -> str:
    """creates a .spec file that is confirmed to work with code-signing

    :param app_name: the name of your app (will output as app_name.app once built)
    :type app_name: str
    :param app_bundle_identifier: identifier registered on https://developer.apple.com
    :type app_bundle_identifier: str
    :param main_python_file: the entry python script, such as app.py or main.py
    :type main_python_file: str
    :param spec_path: where to put the .spec file; if None, uses current working directory, defaults to None
    :type spec_path: str
    :return: if succeessful, the full path to the .spec file
    :rtype: str
    """
    if app_name[-4:] == ".app":
        name = app_name[:-4]
    else:
        name = app_name
    if spec_path==None:
        location = os.getcwd()
    else:
        location = spec_path
    command = ["pyi-makespec", f"{main_python_file}", '--name', f'{name}', "--windowed", "--specpath", f'{location}', "--osx-bundle-identifier", f'{app_bundle_identifier}']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error:
        return os.path.abspath(os.path.join(spec_path, name+".spec"))

def make_default_entitlements(path:str=None) -> str:
    """create the minimum entitlements.plist file for PyInstaller-bundled applications.

    :param path: where to put the entitlements file; if None, uses current working directory, defaults to None
    :type path: str, optional
    :return: if succeessful, the full path to the entitlements file
    :rtype: str
    """
    logger.debug(f"running make_default_entitlements(path={path})")
    location = None
    if path != None:
        location = os.path.join(path, entitlements_file.filename)
    else:
        location = os.path.join(os.getcwd(), entitlements_file.filename)
    try:
        with open(location, "w") as entitlements:
            entitlements.writelines(entitlements_file.contents)
    except FileNotFoundError as e:
        logger.error(f"'{path}' does not exist")
        traceback.print_exc()
    else:
        logger.info(f"wrote entitlements file to '{location}'")
        return location


class Builder():
    def validate(self) -> bool:
        """validate the Builder based on current variables; logs warnings if any detected.

        :return: returns True if no warnings, returns False if warnings detected
        :rtype: bool
        """
        errors = False
        if not os.path.exists(self.main_file) or self.main_file[-3:]!=".py":
            logger.warning(f"unable to find python file at '{self.main_file}'")
            errors = True
        if not re.fullmatch(email_regex, self.apple_developer_email):
            logger.warning(f"invalid email detected: '{self.apple_developer_email}'")
            errors = True
        if not re.search(identifier_regex, self.app_bundle_identifier):
            logger.warning(f"invalid app-bundle-identifier detected (only letters, '.', and '-'): '{self.app_bundle_identifier}'")
            errors = True
        if not os.path.exists(self.spec_file) or self.spec_file[-5:]!=".spec":
            logger.warning(f"unable to find valid spec file at '{self.spec_file}'")
            errors = True
        if not os.path.exists(self.entitlements) or self.entitlements[-6:]!=".plist":
            logger.warning(f"unable to find valid entitlements file at '{self.spec_file}'")
            errors = True
        if re.match(hash_regex, self.developer_id_application_hash):
            logger.warning(f"improper developer_id_application hash detected: '{self.developer_id_application_hash}'")
            errors=True
        if re.match(hash_regex, self.developer_id_installer_hash):
            logger.warning(f"improper developer_id_installer hash detected: '{self.developer_id_installer_hash}'")
            errors=True
        if not errors:
            logger.info(f"no warnings detected for {self}!")
        return not errors

    def __init__(self, main_file:str, app_name:str, app_bundle_identifier:str, apple_developer_email:str, 
                 developer_id_application_hash:str, developer_id_installer_hash:str, spec_file:str=None, 
                 create_spec_file_at:str=None, entitlements_file:str=None, 
                 create_entitlements_file_at:str=None) -> None:
        super().__init__()
        self.main_file = main_file
        self.app_name = app_name
        self.apple_developer_email = apple_developer_email
        self.app_bundle_identifier = app_bundle_identifier
        self.developer_id_application_hash = developer_id_application_hash
        self.developer_id_installer_hash = developer_id_installer_hash
        if spec_file==None:
            self.spec_file = make_spec(self.app_name, self.app_bundle_identifier, self.main_file, create_spec_file_at)
        else:
            self.spec_file = spec_file
        if entitlements_file==None:
            self.entitlements = make_default_entitlements(create_entitlements_file_at)
        else:
            self.entitlements = entitlements_file
        self.validate()

    def build_app(self, no_confirm=True) -> bool:
        """build .app file

        :param no_confirm: whether or not to replace existing build and dist directories; if you chnage to False, please note that the build will fail if these directories are not empty, defaults to True
        :type no_confirm: bool, optional
        :return: whether or not the build completed without most errors (pyinstaller errors are not caught)
        :rtype: bool
        """
        if not self.validate():
            cont = input("warning detected! continue (y/n): ")
            if cont != "y":
                return
        start = time.time()
        command = ["pyinstaller", f"{self.spec_file}"]
        if no_confirm:
            command.append("-y")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        output, error = process.communicate()
        end = time.time()
        if error:
            logger.error("unable to build")
            return False
        else:
            t = round((end-start), 2)
            logger.info(f"build completed ({t} seconds)")
            return True
    
    def sign_app(self) -> None:
        path = os.path.join(os.getcwd(), "dist", f"{self.app_name}.app")
        if(os.path.exists(path)):
            start = time.time()
            command = ["codesign", "--deep", "--force", "--timestamp", "--options", "runtime", "--entitlements", f"{self.entitlements}", "--sign", f"{self.developer_id_application_hash}", f"{path}"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
            end = time.time()
            if error:
                logger.error("unable to sign")
                return False
            else:
                t = round((end-start), 2)
                logger.info(f"sign successful ({t} seconds)")
                return True
        else:
            logger.error(f"unable to find .app file at '{path}'")

class Packager():
    def __init__(self, package_identifier:str, developer_id_installer_hash:str=None) -> None:
        self.package_identifier = package_identifier
        if developer_id_installer_hash != None:
            self.developer_id_installer_hash = developer_id_installer_hash
    
    @property
    def builder(self, _builder:Builder) -> None:
        # set all of the init optional properties on each setting of builder
        self._builder = _builder

    @builder.getter
    def builder(self) -> Builder:
        return self._builder

    def inherit_from_builder(self, builder:Builder) -> None:
        self.builder = builder
        self.developer_id_installer_hash = builder.developer_id_installer_hash

    def build_pkg(self, version:str, uses_scripts:bool=False, scripts_directory:str=None) -> bool:
        command = ["pkgbuild", 
        "--identifier", f"{self.package_identifier}", 
        "--sign", f"{self.developer_id_installer_hash}", 
        "--version", version,
        "--root", "$APP_PATH",
        "--install-location", '/Applications/"$APP_NAME".app']
        # scripts directory must end in "Scripts/" and contain preinstall and postinstall
        # both scripts must be executable -> I NEED TO CODE THIS CHECK FEATURE
        if uses_scripts:
            command.append("--scripts")
            command.append("$SCRIPTS")
        command.append("$TMP_PKG_PATH")