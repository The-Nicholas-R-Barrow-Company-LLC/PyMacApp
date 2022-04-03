# PyMacApp
```pip3 install PyMacApp```

This Repo creates a project that you can clone to streamline MacOS python desktop app development. It contains all necessary scripts to build your final project, as well as code-sign them from Apple (Developer Account required for some features).

# Quickstart: Building & Packaging Your App
```
from pymacapp.app import App
from pymacapp.package import Package


APPLE_DEVELOPER_EMAIL = 
APP_SPECIFIC_PASSWORD = 

app = App("My New App")
app.config("./src/main.py").build().sign(App.get_first_hash())

package = Package(app, identifier="com.nicholasrbarrow.ital.pkg")
package.build().sign(Package.get_first_hash()).notorize(APPLE_DEVELOPER_EMAIL, APP_SPECIFIC_PASSWORD).wait()
```
## Currently supports
This currently supports (and has been tested on) Python 3.9.9 on MacOS 11.6. This tool may work on other systems, but has not been tested.
Feature (release phase):
- Building .app files (beta)
- Adding custom files/resources to app files (alpha)
- Signing .app files (beta)
- Building .pkg files (beta)
- Signing .pkg files (alpha)
- Notorizing .pkg files (alpha)
- Stapling .pkg files (alpha)
- Custom build commands, natively in Python (beta)

# Full Setup (Code-signing)
## Precursor - PyPi: PyMacApp
```pip3 install PyMacApp```
- Uses PyInstaller, should install automatically

## Precursor - Xcode
Make sure to have xcode installed, and verify that the xcode command line tools are installed: 
- ```xcode-select --install```

## Part 1: Developer Account
Note: This section is taken from: https://gist.github.com/txoof/0636835d3cc65245c6288b2374799c43
### (1/2) Create a developer account with Apple
- Go to https://developer.apple.com and shell out $99 for a developer account
- Download and install X-Code from the Apple App Store
- Open and run X-Code app and install whatever extras it requires
- Open the preferences pane (cmd+,)
- click the + in the lower right corner
choose Apple ID
- enter your apple ID and password
### (2/2) Create an App-Specific password
- Instructions from Apple to create: https://support.apple.com/en-us/HT204397
- Save this password (you will need it for notorizing)

## Part 2: Get Your Hashes
### (1/3) Create Certificates with XCode
- Open XCode
- In the top-apple Menu, go to XCode > Preferences > Accounts > Your Account > In the team, chose the Admin team > Manage Certificates in the bottom-right
- click the plus in the bottom corner
- choose "Developer ID Application"
- repeating, click the plus in the bottom corner
- choose "Developer ID Installer"
### (2/3) Get Certificates and Add to Project
#### Note: as of version 2.0.0, you should use ```the App.get_first_hash() and Package.get_first_hash()``` to get your hashes in your ```build.py``` script
- to manually get hashes, run:
> ```security find-identity -p basic -v```
- your output will look like:
> 1) HASH_OF_ID_HERE "Developer ID Application: ..."
> 2) HASH_OF_ID_HERE "Developer ID Installer: ..."
> 
>    2 valid identities found
- copy the appropriate hashes or simply use ```get_first_application_hash()``` or ```get_first_installer_hash()``` by importing them (```from pymacapp.helpers import get_first_application_hash, get_first_installer_hash```)
### (3/3) Create your Identifiers
- developer.apple.com
- choose "account" in top right
- login
- "Certificates, IDs, and Profiles"
- on the left, switch to "Identifiers"
- create two App IDs, one for your .app and one for your .pkg
- it may be helpful to do something like ```com.your-domain.app-name``` for the .app and ```com.your-domain.app-name.pkg``` for the .pkg
# Coding Your App
Code your app however you'd like. You'll need to identify a main script file (main.py or app.py); where ever you run your program from, that is your main script file.
# Advanced Customization
## Pre- and Post-Install Scripting
Better docs coming soon; see example under Quickstart.

# Project History
This project began while performing work for Georgetown University's Department of Italian Studies. The code herein was needed to develop applications within the Department. Some of the code contains outside work, so this was a joint collaboration. 

## Changelog
### [1.1.1] 03.19.2022
- added changelog to readme
- updated readme's quick-start example
- cleaned the pymacapp directory (removed unsupported beta and old content)
- added docstrings to all functions of App and Package
- added function to output log if notary service fails during Package.notorize(...).wait(...)
### [1.2.0] 03.20.2022
- added alpha-feature: Resource (```from pymacapp import Resource```). This feature allows you to add custom files to your application using the App.resource(...) method. 
### [1.2.1] 03.22.2022
- added alpha-feature: custom commands (```from pymacapp.custom import bash```)
- note: Resource feature is experiencing bug that is not yet patched.
### [1.2.2] 03.22.2022
- patching release 1.2.1
- note: Resource feature is experiencing bug that is not yet patched.
### [1.2.3] 03.26.2022
- relocating custom commands (```from pymacapp.command import cmd```) and moving to beta
- removing: Resource feature introduced in 1.2.0
### [1.2.4] 03.26.2022
- bug fixes
- moving some ```subprocess``` commands from ```subprocess.Popen(...)``` to a custom function which uses ```subprocess.run(...)```
- updating README
### [1.2.5] 03.27.2022
- added: new coverage for py-makespec (included with pyinstaller)
- deprecated: App.setup(...); see below
- added: App.config(...) to use new coverage for py-makespec
### [1.2.6] 03.27.2022
- minor bug fixes to new validators
### [1.2.7] 03.27.2022
- minor bug fixes to new coverage for py-makespec
### [1.2.8] 03.27.2022
- minor bug fixes to new coverage for py-makespec
### [1.2.9] 03.27.2022
- minor bug fixes to new coverage for py-makespec
### [1.3.0] 03.28.2022
- added: ```pymacapp.versioning.VersionLocker```. This feature allows you to set a version (an unlimited-length string of non-negative integers delimited by periods ('.')) and pymacapp will store the version number in a file whenever its ```.lock()``` method is called (this is useful so that you can decide when to lock the version (i.e. do not lock until after the app successfully builds, successfully packages, etc.)).
### [2.0.1] 04.01.2022
- reformatted major sections of the code to better structure the project for maintaining into the future
- completed migration to modern ```subprocess``` utilization
### [2.0.2] 04.01.2022
- fixed README to reflect 2.0.1 changes
### [2.0.3] 04.03.2022
- fixed a bug where default ```entitlements.plist``` did not package
### [2.0.4] 04.03.2022
- continuing to fix a bug where default ```entitlements.plist``` did not package
### [2.0.5] 04.03.2022
- continuing to fix a bug where default ```entitlements.plist``` did not package
### [2.0.6] 04.03.2022
- fixing bug related to Scripts collecting
### [2.0.7] 04.03.2022
- fixing bug related to Scripts collecting
### [2.0.8] 04.03.2022
- fixing bug related to Scripts being made executable in non-terminal environments (i.e. PyCharm)