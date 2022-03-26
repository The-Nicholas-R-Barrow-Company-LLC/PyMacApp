import subprocess, os
from .logger import logger
from .command import cmd

MINIMUM_ENTITLEMENTS = os.path.join(os.path.dirname(__file__), "entitlements.plist")

# All scripts should be copied into this folder
COLLECT_SCRIPTS_HERE = os.path.join(os.path.dirname(__file__), "Scripts/")

def get_first_application_hash(output:bool=False) -> str:
    """equivalent to running "security find-identity -p basic -v" in terminal and looking for the hash next to "Developer ID Application"

    :param output: log output and errors from the command to find the application hash, defaults to False
    :type output: bool, optional
    :return: the Developer ID Application hash
    :rtype: str
    """    
    command = "security find-identity -p basic -v"
    
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    process, output, error = cmd(command, suppress_log=not output)
    if not error: 
        lines = output.splitlines()
        for line in lines:
            if "Developer ID Application" in str(line):
                h = line.split()[1]
                return h
    else:
        logger.debug(f"an error occurred: {error}")

def get_first_installer_hash() -> str:
    """equivalent to running "security find-identity -p basic -v" in terminal and looking for the hash next to "Developer ID Installer"

    :return: the Developer ID Installer hash
    :rtype: str
    """
    command = ["security", "find-identity", "-p", "basic", "-v"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error: 
        lines = output.splitlines()
        for line in lines:
            if "Developer ID Installer" in str(line):
                h = line.split()[1]
                return (h).decode()

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
        # logger.debug(f"spec_path:{location}")
        # logger.debug(f"name:{name}")
        logger.info(f"wrote spec file to '{os.path.join(location, name+'.spec')}'")
        return os.path.abspath(os.path.join(location, name+".spec"))

def make_spec_with_datas(app_name:str, app_bundle_identifier:str, main_python_file:str, spec_path:str, datas:list) -> str:
    """creates a .spec file that is confirmed to work with code-signing

    :param app_name: the name of your app (will output as app_name.app once built)
    :type app_name: str
    :param app_bundle_identifier: identifier registered on https://developer.apple.com
    :type app_bundle_identifier: str
    :param main_python_file: the entry python script, such as app.py or main.py
    :type main_python_file: str
    :param spec_path: where to put the .spec file; if None, uses current working directory, defaults to None
    :type spec_path: str
    :param datas: list of datas in form of (current_path, {folder in .app to put file at current_path})
    :type datas: list
    :return: if succeessful, the full path to the .spec file
    :rtype: str
    """
    if app_name[-4:] == ".app":
        name = app_name[:-4]
    else:
        name = app_name
    if name[-5:] == ".spec":
        name = name[:-5]
    if spec_path==None:
        location = os.getcwd()
    else:
        location = spec_path
    command = ["pyi-makespec", f"{main_python_file}", '--name', f'{name}', "--windowed", "--specpath", f'{location}', "--osx-bundle-identifier", f'{app_bundle_identifier}']
    for data in datas:
        command.append("--add-data")
        command.append(f"{data[0]}:{data[1]}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
    output, error = process.communicate()
    if not error:
        logger.info(f"wrote spec file to '{os.path.join(location, name+'.spec')}'")
        return os.path.abspath(os.path.join(location, name+".spec"))

