from pymacapp import App, Package
from pymacapp.logger import set_level
from pymacapp.helpers import get_first_application_hash
from pymacapp.scripthelpers import DefaultPostinstallScript, DefaultPreinstallScript
import logging

# set logging level
set_level(logging.INFO)

app = App(name="My First App", identifier="com")
app.setup(script="./test/main.py").build().sign(get_first_application_hash()).verify()

package = Package(app, "com.pkg")
preinstall_script = DefaultPreinstallScript()
postinstall_script = DefaultPostinstallScript(app._name)
package.build(preinstall_script.path(), postinstall_script.path())
