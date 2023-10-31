from pymacapp.buildtools.app import App
from pymacapp.buildtools.package import Package
import os

# CREDENTIALS
APPLE_DEVELOPER_EMAIL = os.environ["APPLE_EMAIL"]
APPLE_DEVELOPER_TEAM_ID = os.environ["APPLE_DEVELOPER_TEAM_ID"]
APPLE_APP_SPECIFIC_PASSWORD = os.environ["APPLE_APP_SPECIFIC_PASSWORD"]
APP_HASH = App.get_first_hash()
PKG_HASH = Package.get_first_hash()

assert APPLE_DEVELOPER_EMAIL
assert APPLE_DEVELOPER_TEAM_ID
assert APPLE_APP_SPECIFIC_PASSWORD
assert APP_HASH
assert PKG_HASH

# For example purposes, building path to the main.py file under PyMacApp/example/src/main.py
pardir = os.path.dirname(__file__)
srcdir = os.path.join(pardir, "src")
main = os.path.join(srcdir, "main.py")  # ./src/main.py, but as absolute path

# create the app wrapper
app = App("My New App")
app.config(main).build().sign(APP_HASH)

# create the package wrapper
package = Package(app, identifier="foo.bar")
# explicit authentication required starting in v.4.0.1
package.login(APPLE_DEVELOPER_EMAIL, APPLE_APP_SPECIFIC_PASSWORD, APPLE_DEVELOPER_TEAM_ID)
package.build().sign(Package.get_first_hash()).notarize()
package.log_full_notary_log()
package.staple()
