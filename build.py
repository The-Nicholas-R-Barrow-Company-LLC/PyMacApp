# default build script
from pymacapp import Builder
from pymacapp.buildtools import get_first_application_hash, get_first_installer_hash

## to change the logging level, uncomment the lines below and set the level (0, 10, 20, 30, 40, 50)
# from pymacapp.buildtools import logger
# logger.setLevel(20)

main_script = "./app/app.py"
app_name = "My Shiny New App"
app_identifier = "com.app"

builder = Builder(main_file=main_script, app_name=app_name, app_bundle_identifier=app_identifier)

builder.build_app()