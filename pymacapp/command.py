import subprocess, os
from subprocess import CompletedProcess
from .logger import logger

class Command:
    def __init__(self, process:CompletedProcess) -> None:
        self.process = process
        self.output = self.process.stdout
        self.error = self.process.stderr
    
    def __getitem__(self, item):
        if item == 0:
            return self.process
        elif item == 1:
            return self.output
        elif item == 2: 
            return self.error
        else:
            raise IndexError("Object only has three indices: \n[0] process:subprocess.CompletedProcess\n[1] output:str\n[2] error:str")

    def __str__(self) -> str:
        return subprocess.list2cmdline(self.process.args)
    
    def recover_command(self) -> 'list[str]':
        """return the list of arguments send to the executable; use str(Output) to recover the full command-line as a string

        :return: argument list used in a command
        :rtype: list[str]
        """
        r:list[str] = self.process.args
        return r


def cmd(cmd:str, executable:str='/bin/bash', cwd:str=os.getcwd(), suppress_log = False):
    if not suppress_log:
        logger.debug(f"attempting to execute '{cmd}' using '{executable}' in '{cwd}'")
    if os.access(executable, os.X_OK):
        if os.path.isdir(cwd):
            try:
                process = subprocess.run(cmd, shell=True, executable=executable, cwd=cwd, capture_output=True, text=True)
            except Exception as e:
                logger.warning(f"an exception occurred while trying to execute command: {e}")
            else:
                if not suppress_log:
                    logger.info(f"process will be returned as an Output object in index 0")
                if process.stdout and not suppress_log:
                        logger.info(f"BEGIN OUTPUT FROM COMMAND: \n{process.stdout}")
                        logger.info(f"END OUTPUT FROM COMMAND")
                        logger.info(f"output will be returned as an Output object in index 1")
                if process.stderr and not suppress_log:
                    logger.error(f"BEGIN OUTPUT FROM COMMAND: \n{process.stderr}")
                    logger.error(f"END OUTPUT FROM COMMAND")
                    logger.info(f"error will be returned as an Output object in index 2")
                return Command(process)
                
        else:
            logger.error(f"'{cwd}' is not a directory")
            raise RuntimeError()
    else:
        logger.error(f"'{executable}' is not an executable")
        raise RuntimeError()