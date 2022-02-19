import os
from tkinter import Pack
from .buildtools import Builder as Builder
from .buildtools import Packager as Packager

class AppFactory():
    def init_builder():
        pass
    def init_packager():
        pass
    def init_notary_agent():
        pass

def make_config_file() -> None:
    with open(os.path.join(os.getcwd(), "boilerplate.cfg"), "w") as f:
        f.writelines("""
app_name=
app_bundle_identifier=
apple_developer_email=
developer_id_application_hash=
developer_id_installer_hash=
spec_file=None
create_spec_file_at=None
entitlements_file=None
create_entitlements_file_at=None
""")

# def BuildDefaultApp():
#     # do everything to create a blank app, including an app.py file
#     pass 

# class AppFactory(Builder, Packager):
#     def __init__(self, main_file: str, app_name: str, app_bundle_identifier: str, apple_developer_email: str, developer_id_application_hash: str, developer_id_installer_hash: str, spec_file: str = None, create_spec_file_at: str = None, entitlements_file: str = None, create_entitlements_file_at: str = None) -> None:
#         super().__init__(main_file, app_name, app_bundle_identifier, apple_developer_email, developer_id_application_hash, developer_id_installer_hash, spec_file, create_spec_file_at, entitlements_file, create_entitlements_file_at)