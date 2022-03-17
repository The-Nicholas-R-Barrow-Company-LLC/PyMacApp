import re, os, subprocess
from .errors import ConfigAttributeError, ConfigEmptyValueError
from .logger import logger
from .models import App

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
identifier_regex = "^[a-zA-Z0-9\-.]+$"
hash_regex = "^[A-Z0-9]*$"


def make_spec(app_name:str, app_bundle_identifier:str, main_python_file:str, spec_path:str, file_name:str) -> str:
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
    if file_name:
        name = file_name
    if name[-5:] == ".spec":
        name = name[:-5]
    if spec_path==None:
        location = os.getcwd()
    else:
        location = spec_path
    command = ["pyi-makespec", f"{main_python_file}", '--name', f'{name}', "--windowed", "--specpath", f'{location}', "--osx-bundle-identifier", f'{app_bundle_identifier}']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error:
        logger.debug(f"spec_path:{location}")
        logger.debug(f"name:{name}")
        logger.info(f"wrote spec file to '{os.path.join(location, name+'.spec')}'")
        return os.path.abspath(os.path.join(location, name+".spec"))


class BaseConfig:
    def __init__(self, app:App=None, app_name:str=None) -> None:
        if not app and not app_name:
            logger.error("must pass either app or app_name to Config")
        elif app:
            self.__name = app.name
        if app_name == None or app_name == "":
            raise ConfigEmptyValueError
        elif app_name[-4:] == ".app":
            logger.warning(f"{self}.name should not end in '.app'; the '.app' extension will be ignored")
            self.__name = app_name[:-4]
        else:
            self.__name = app_name

class BuildConfig(BaseConfig):
    def __init__(self, app: App = None, app_name: str = None) -> None:
        super().__init__(app, app_name)
        self.__app_identifier:str = None
        self.__spec:str = None
        self.__entry:str = None
        self.__source_directory:str = None
        return None
    
    def setup(self, entry:str, spec:str=None, identifier:str=None):
        self.entry = entry
        self.spec = spec
        self.app_identifier = identifier
        return self
    
    @property
    def entry(self) -> str:
        return self.__entry
    @entry.setter
    def entry(self, value) -> None:
        if os.path.exists(value):
            if value[-3:] == ".py":
                self.__entry = value
                self.__source_directory = os.path.dirname(value)
            else:
                raise ConfigAttributeError(f"file '{value}' is not a .py file")
        else:
            raise ConfigAttributeError(f"file '{value}' does not exist")
    @entry.deleter
    def entry(self) -> None:
        raise ConfigAttributeError("cannot delete attribute 'entry'")

    @property
    def spec(self) -> str:
        return self.__spec
    @spec.setter
    def spec(self, value:str=None) -> None:
        if value:
            if os.path.exists(value):
                if value[-5:] == ".spec":
                    self.__spec = value
                else:
                    raise ConfigAttributeError(f"file '{value}' is not a .spec file")
            else:
                raise ConfigAttributeError(f"file '{value}' does not exist")
        else:
            path = os.path.join(self.__source_directory,"build.spec")
            if os.path.exists(path):
                self.__spec = path
                logger.warning(f"'{path}' exists, file will be used; delete this file if you want to re-generate it, no changes have been made")
                # warnings.warn(f"'{path}' exists, file will be used; delete this file if you want to re-generate it, no changes have been made")
            else:
                # NOTE: need to fix my make_spec function so that I can specify the name of the spec file
                v = make_spec(self.name, self.app_identifier, self.entry, self.__source_directory, "build.spec")
                if v:
                    self.__spec = v
                else:
                    raise RuntimeError(f"unable to create 'build.spec' file in '{self.__source_directory}'")
    @spec.deleter
    def spec(self) -> None:
        raise ConfigAttributeError("cannot delete attribute 'spec'")
    
    @property
    def app_identifier(self) -> str:
        return self.__app_identifier
    @app_identifier.setter
    def app_identifier(self, value) -> None:
        try:
            if not re.search(identifier_regex, value):
                # warnings.warn(f"invalid identifier detected (only letters, '.', and '-'): '{value}'")
                logger.warning(f"invalid identifier detected (only letters, '.', and '-'): '{value}'")
        except:
            # warnings.warn(f"unable to validate: app_identifier")
            logger.warning(f"unable to validate: app_identifier")
        self.__app_identifier = value
    @app_identifier.deleter
    def app_identifier(self) -> None:
        del self.__app_identifier

class PackageConfig(BaseConfig):
    def __init__(self, name: str) -> None:
        """a config object for .pkg-related objects

        :param name: the name of your application
        :type name: str
        """
        super().__init__(name)
        # self.__unsigned_package_directory:str = None
        self.__signed_package_directory:str = None
    
    def setup(self, signed_package_directory:str) -> None:
        self.signed_package_directory = signed_package_directory
    
    @property
    def signed_package_directory(self) -> str:
        return self.__signed_package_directory

    @signed_package_directory.setter
    def signed_package_directory(self, value) -> None:
        if not os.path.isdir(value):
            raise ConfigAttributeError(f"directory '{value}' is not an existing directory")
        else:
            self.__signed_package_directory = value