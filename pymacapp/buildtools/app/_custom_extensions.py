import plistlib
from ...logger import logger
import os
from dataclasses import dataclass
from ...command import Command


@dataclass(frozen=True)
class LSHandlerRank:
    Owner = "Owner"
    Default = "Default"
    Alternate = "Alternate"
    NA = "None"


@dataclass(frozen=True)
class CFBundleTypeRole:
    Editor = "Editor"
    Viewer = "Viewer"
    Shell = "Shell"
    QLGenerator = "QLGenerator"
    NA = "None"


class UTIExtension:

    def __init__(self, ext: str, rank: LSHandlerRank = LSHandlerRank.Alternate, role: CFBundleTypeRole = CFBundleTypeRole.Viewer, validate: bool = True):
        """
        Create a UTI Extension object; find valid ones locally using UTIExtensions.find_local(...) or go to https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/UTIRef/Articles/System-DeclaredUniformTypeIdentifiers.html#//apple_ref/doc/uid/TP40009259-SW1
        :param ext: a valid UTI extension
        """
        if validate:
            if ext not in self.find_local(ext):
                logger.warning(f"extension '{ext}' is not currently registered on this machine; may not be valid")
        self.ext = ext
        self.rank = rank
        self.role = role

    def __repr__(self):
        return self.ext

    def __str__(self):
        return self.ext

    @staticmethod
    def find_local(search: str) -> "list[str]":
        """
        Search the local machine for all registered UTIs containing 'search'
        :param search: the (sub)string to search for
        :return: a list of matches (strings)
        """
        logger.info(f"searching for '{search}'")
        proc, out, err = Command.run("/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -dump", suppress_log=True)
        possible_utis = []
        for line in out.splitlines():
            if "uti" in line[0:3]:
                uti = (line.split(":")[1]).strip()
                if search in uti:
                    logger.debug(f"found possible uti for '{search}': '{uti}'")
                    if uti not in possible_utis:
                        possible_utis.append(uti)
        logger.info(f"found {len(possible_utis)} possible utis (returned as list)")
        return possible_utis

    @staticmethod
    def add_custom_doc_types(pl_file: str, extensions: "list[UTIExtension]"):
        """
        add a list of extensions to a plist file
        :param pl_file: the Info.plist file to add to
        :param extensions: list of UTIExtensions
        :return: True (if finishes without error)
        """
        # load the plist and init
        pl = None
        with open(pl_file, 'rb') as fp:
            pl = plistlib.load(fp)
        os.remove(pl_file)
        logger.debug(f"loaded Info.plist: {pl}")

        # add the data
        pl['CFBundleDocumentTypes'] = []
        for ext in extensions:
            logger.debug(f"attempting to add document type '{ext}' to info.plist")
            try:
                file_ext = str(ext).split(".")[-1:][0]
            except Exception as e:
                file_ext = str(ext)
            pl['CFBundleDocumentTypes'].append({
                'CFBundleTypeName': f"{str(ext)}",
                'CFBundleTypeRole': ext.role,
                'LSHandlerRank': ext.rank,
                'LSItemContentTypes': [str(ext)],
                'CFBundleTypeExtensions': [file_ext]
            })

        # save data
        with open(pl_file, 'w') as fp:
            pass
        with open(pl_file, 'wb') as fp:
            plistlib.dump(pl, fp)

        # done
        return True
