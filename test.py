from pymacapp.new import App, Package
from pymacapp.new.logger import set_level
from pymacapp.new.helpers import get_first_application_hash

set_level(20)

app = App(name="My First App", identifier="com")
app.setup(script="./test/main.py").build().sign(get_first_application_hash())
# app.all()

package = Package(app, "com.pkg")
package.build().sign().notorize().wait().staple()
# package.all()
