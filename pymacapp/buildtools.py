import subprocess, os, traceback, re, time
from .defaultscripts import entitlements as entitlements_file
from .logger import logger
from .setuptools import BuildConfig, PackageConfig, make_spec
import warnings
import functools

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
identifier_regex = "^[a-zA-Z0-9\-.]+$"
hash_regex = "^[A-Z0-9]*$"

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

def get_first_application_hash() -> None:
    command = ["security", "find-identity", "-p", "basic", "-v"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error: 
        lines = output.splitlines()
        for line in lines:
            if "Developer ID Application" in str(line):
                h = line.split()[1]
                return (h).decode()
    else:
        logger.debug(f"an error occurred: {error}")

def get_first_installer_hash() -> None:
    command = ["security", "find-identity", "-p", "basic", "-v"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error: 
        lines = output.splitlines()
        for line in lines:
            if "Developer ID Installer" in str(line):
                h = line.split()[1]
                return (h).decode()

def list_signing_hashes() -> None:
    """lists signing hashes to console by calling 'security find-identity -p basic -v'
    """
    command = ["security", "find-identity", "-p", "basic", "-v"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error: 
        lines = output.splitlines()
        for line in lines:
            if "Developer ID Application" in str(line):
                h = line.split()[1]
                logger.info(f"valid 'developer_id_application_hash' hash found: {(h).decode()}")
            if "Developer ID Installer" in str(line):
                h = line.split()[1]
                logger.info(f"valid 'developer_id_installer_hash' hash found: {(h).decode()}")
    else:
        logger.debug(f"an error occurred: {error}")



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

@deprecated
class Builder():
    def validate(self) -> bool:
        """validate the Builder based on current variables; logs warnings if any detected.

        :return: returns True if no warnings, returns False if warnings detected
        :rtype: bool
        """
        errors = False
        try:
            if not os.path.exists(self.main_file) or self.main_file[-3:]!=".py":
                logger.warning(f"unable to find python file at '{self.main_file}'")
                errors = True
        except:
            logger.warning(f"unable to validate: main_file")
            errors=True
        try:
            if not re.search(identifier_regex, self.app_bundle_identifier):
                logger.warning(f"invalid app-bundle-identifier detected (only letters, '.', and '-'): '{self.app_bundle_identifier}'")
                errors = True
        except:
            logger.warning(f"unable to validate: app_bundle_identifier")
            errors=True
        try:
            if not os.path.exists(self.spec_file) or self.spec_file[-5:]!=".spec":
                logger.warning(f"unable to find valid spec file at '{self.spec_file}'")
                errors = True
        except:
            logger.warning(f"unable to validate: spec_file")
            errors=True
        try:
            if not os.path.exists(self.entitlements) or self.entitlements[-6:]!=".plist":
                logger.warning(f"unable to find valid entitlements file at '{self.spec_file}'")
                errors = True
        except:
            logger.warning(f"unable to validate: entitlements")
            errors=True
        try:
            if not re.match(hash_regex, self.developer_id_application_hash):
                logger.warning(f"improper developer_id_application hash detected: '{self.developer_id_application_hash}'")
                errors=True
        except:
            logger.warning(f"unable to validate: developer_id_application_hash")
            errors=True
        if not errors:
            logger.info(f"no warnings detected for {self}!")
        else:
            logger.warning(f"errors detected during validation; surpress this message with validate=False")
        return not errors

    def __init__(self, 
                main_file:str, 
                app_name:str, 
                app_bundle_identifier:str=None, 
                developer_id_application_hash:str=None,  
                spec_file:str=None, 
                create_spec_file_at:str=None, 
                entitlements_file:str=None, 
                create_entitlements_file_at:str=None,
                validate:bool=True) -> None:
        super().__init__()
        self.main_file = main_file
        self.app_name = app_name
        self.app_bundle_identifier = app_bundle_identifier
        self.developer_id_application_hash = developer_id_application_hash
        if spec_file==None:
            self.spec_file = make_spec(self.app_name, self.app_bundle_identifier, self.main_file, create_spec_file_at)
        else:
            self.spec_file = spec_file
        if entitlements_file==None:
            self.entitlements = make_default_entitlements(create_entitlements_file_at)
        else:
            self.entitlements = entitlements_file
        if validate:
            self.validate()
        else:
            logger.debug("validation is disabled")

    def build_app(self, no_confirm=True, validate=True) -> bool:
        """build .app file

        :param no_confirm: whether or not to replace existing build and dist directories; if you chnage to False, please note that the build will fail if these directories are not empty, defaults to True
        :type no_confirm: bool, optional
        :return: whether or not the build completed without most errors (pyinstaller errors are not caught)
        :rtype: bool
        """
        if validate:
            if not self.validate():
                cont = input("warning detected! continue (y/n): ")
                if cont != "y":
                    return
        else:
            logger.debug("validation is disabled")
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
    
    def sign_app(self) -> bool:
        """signs a .app file

        :return: if the .app successfully signed
        :rtype: bool
        """
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

class Bundler():
    def __init__(self, config:BuildConfig) -> None:
        self.config = config
        logger.info(f"Bundler created: {self}")
    
    def build(self) -> None:
        logger.info(f"{self}.build() method initialized")

    def sign(self) -> None:
        logger.info(f"{self}.sign() method initialized")

@deprecated
class Packager():

    def validate(self) -> bool:
        """validate the Packager based on current variables; logs warnings if any detected.

        :return: returns True if no warnings, returns False if warnings detected
        :rtype: bool
        """
        errors = False
        try:
            pass
        except:
            pass
        if not errors:
            logger.info(f"no warnings detected for {self}!")
        else:
            logger.warning(f"errors detected during validation; surpress this message with validate=False")
        return not errors

    def __init__(self, 
                package_identifier:str, 
                version:str,
                developer_id_installer_hash:str, 
                use_scripts:bool=False,
                scripts_path:str=None,
                builder:Builder=None, 
                app_name:str=None,
                app_path:str=None,
                install_directory:str="/Applications/"
                ) -> None:
        self.package_identifier = package_identifier
        self.version = version
        self.developer_id_installer_hash = developer_id_installer_hash
        if use_scripts:
            if os.path.exists(scripts_path):
                self.scripts = scripts_path
            else:
                logger.error(f"unable to find scripts_path '{scripts_path}'; scripts will be ignored")
        if builder:
            if app_name or app_path:
                logger.warning(f"since 'builder' is provided, app_name and app_path are ignored")
            self.app_name = builder.app_name
            self.app_path = os.path.join(os.getcwd(), "dist", f"{self.app_name}.app")
        elif app_name and app_path:
            if app_name[-4:] == ".app":
                self.app_name = app_name[:-4]
            else:
                self.app_name = app_name
                self.app_path = os.path.join(os.getcwd(), "dist", f"{self.app_name}.app")
        else:
            logger.warning(f"must specify either (1) builder or (2) app_name and app_path")

    def build_pkg(self, version:str, uses_scripts:bool=False, scripts_directory:str=None) -> bool:
        command = ["pkgbuild", 
                    "--identifier", f"{self.package_identifier}", 
                    "--sign", f"{self.developer_id_installer_hash}", 
                    "--version", version,
                    "--root", "$APP_PATH",
                    "--install-location", '/Applications/"$APP_NAME".app',
                    "TMP"]
        # scripts directory must end in "Scripts/" and contain preinstall and postinstall
        # both scripts must be executable -> I NEED TO CODE THIS CHECK FEATURE
        if uses_scripts:
            command.append("--scripts")
            command.append("$SCRIPTS")
        command.append("$TMP_PKG_PATH")

class NotaryAgent():
    def __init__(self) -> None:
        pass

class Stapler():
    def __init__(self, config:PackageConfig) -> None:
        self.config = config
        logger.info(f"Stapler created: {self}")

    def staple(self):
        logger.info(f"{self}.staple() method initialized")
        command = ["xcrun", "stapler", "staple", self.config.signed_package_directory]
        debug_command = " ".join(command)
        logger.debug(f"staple command to execute with bash: '{debug_command}'")
        logger.debug(f"attempting to execute staple command with bash")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
        except Exception as e:
            logger.error(f"unable to execute bash command on {self}.staple(): {e}")
        else:
            if error:
                logger.error(f"{self}.staple() encountered an error during the staple process: {error}")
            if output:
                logger.debug(f"output from {self}.staple(): \n{output}")
        finally:
            logger.info(f"exiting {self}.staple()")
    
