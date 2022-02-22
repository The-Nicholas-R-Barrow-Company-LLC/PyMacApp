import re, warnings, os
from .buildtools import make_spec
from .errors import ConfigAttributeError, ConfigEmptyValueError

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
identifier_regex = "^[a-zA-Z0-9\-.]+$"
hash_regex = "^[A-Z0-9]*$"

class BasicConfig():
    def __init__(self, name:str) -> None:
        self.__name:str = name
    @property
    def name(self) -> None:
        return self.__name
    @name.setter
    def name(self, value) -> None:
        if value == None or value == "":
            raise ConfigEmptyValueError
        else:
            self.__name = value
    @name.deleter
    def name(self) -> None:
        raise ConfigAttributeError("cannot delete attribute 'name'")

class BuildConfig(BasicConfig):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__app_identifier:str = None
        self.__spec:str = None
        self.__entry:str = None
    
    def setup(self, entry:str, spec:str=None, identifier:str=None) -> None:
        self.entry = entry
        self.spec = spec
        self.app_identifier = identifier
    
    @property
    def entry(self) -> None:
        return self.__entry
    @entry.setter
    def entry(self, value) -> None:
        if os.path.exists(value):
            if value[-3:] == ".py":
                self.__entry = value
            else:
                raise ConfigAttributeError(f"file '{value}' is not a .py file")
        else:
            raise ConfigAttributeError(f"file '{value}' does not exist")
    @entry.deleter
    def entry(self) -> None:
        raise ConfigAttributeError("cannot delete attribute 'entry'")

    @property
    def spec(self) -> None:
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
            path = os.path.join(os.getcwd(),"build.spec")
            if os.path.exists(os.path.join(os.getcwd(), "build.spec")):
                self.__spec = path
                warnings.warn(f"'{path}' exists, file will be used; delete this file if you want to re-generate it, no changes have been made")
            else:
                # NOTE: need to fix my make_spec function so that I can specify the name of the spec file
                v = make_spec(self.name, self.app_identifier, self.entry, os.getcwd(), "build.spec")
                if v:
                    self.__spec = v
                else:
                    raise RuntimeError(f"unable to create 'build.spec' file in '{os.getcwd()}'")
    @spec.deleter
    def spec(self) -> None:
        raise ConfigAttributeError("cannot delete attribute 'spec'")
    
    @property
    def app_identifier(self) -> None:
        return self.__app_identifier
    @app_identifier.setter
    def app_identifier(self, value) -> None:
        try:
            if not re.search(identifier_regex, value):
                warnings.warn(f"invalid identifier detected (only letters, '.', and '-'): '{value}'")
        except:
            warnings.warn(f"unable to validate: app_identifier")
        self.__app_identifier = value
    @app_identifier.deleter
    def app_identifier(self) -> None:
        del self.__app_identifier

class PackageConfig(BasicConfig):
    def __init__(self, name: str) -> None:
        super().__init__(name)

# class Config():
#     def __init__(self) -> None:
#         # build app

#         # pkg specific
#         self.__install:str = None
#         self.__version:str = None
#         self.__scripts:str = None
#         self.__tmp_location:str = None
#         self.__signed_location:str = None
#         self.__installer_hash:str = None

#     def app(self, name:str, version:str=None, identifier:str=None) -> None:
#         self.__name = name
#         self.__version = version
#         self.__app_identifier = identifier


    
#     @property
#     def install(self) -> None:
#         return self.__install
#     @install.setter
#     def install(self, value) -> None:
#         if value == None or value == "":
#             raise ConfigEmptyValueError
#         elif value[-1:] != "/":
#             raise ConfigAttributeError("install should be a parent directory (ending in '/') where you want your application to be installed.")
#         else:
#             self.__install = value
#     @install.deleter
#     def install(self) -> None:
#         raise ConfigAttributeError("cannot delete attribute 'install'")

#     @property
#     def version(self) -> None:
#         return self.__version
#     @version.setter
#     def version(self, value) -> None:
#         self.__version = value
#     @version.deleter
#     def version(self) -> None:
#         del self.__version
    

    
    # def pkg(self)

if __name__ == "__main__":
    pass
