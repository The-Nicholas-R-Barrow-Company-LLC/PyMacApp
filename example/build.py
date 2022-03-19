from pymacapp import App, Package
from pymacapp.logger import set_level
from pymacapp.helpers import get_first_application_hash, get_first_installer_hash
import logging

APPLE_DEVELOPER_ID_EMAIL = None # fill this in
APP_SPECIFIC_PASSWORD = None # fill this in

# set logging level for pymacapp's built-in logger
set_level(logging.DEBUG)

# create an application object
app = App(name="My First App", identifier="com.identifier")
# setup your app by specifying the main python script ('entry point')
app.setup(script="./src/main.py")
# build your app
app.build()
# sign your app using the first available hash (see Setup for more)
app.sign(get_first_application_hash())


# create a package object
package = Package(app, version="0.1", identifier="com.identifier.pkg")
# build your package
package.build(postinstall_script="./src/Scripts/postinstall")
# sign your package
package.sign(get_first_installer_hash())
# notorize with your apple developer id
package.notorize(APPLE_DEVELOPER_ID_EMAIL, APP_SPECIFIC_PASSWORD)
# wait for the notary agent to respond
    # if valid, it will automatically staple
    # if invalid, it will stop
package.wait()