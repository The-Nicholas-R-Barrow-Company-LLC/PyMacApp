from pymacapp import App, Package
from pymacapp.logger import set_level
from pymacapp.helpers import get_first_application_hash, get_first_installer_hash
import logging

# set logging level
set_level(logging.DEBUG)

app = App(name="My First App", identifier="com")
app.setup(script="./test/main.py").build().sign(get_first_application_hash()).verify()

package = Package(app, version="0.1", identifier="com.pkg")
package.build(output="installer.pkg", postinstall_script="/Users/nicholasbarrow/GitHub/PyMacApp/test/Scripts/postinstall").sign(get_first_installer_hash())
