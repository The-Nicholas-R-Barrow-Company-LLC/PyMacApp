# PyMacApp
```pip3 install PyMacApp```
This Repo creates a project that you can clone to streamline MacOS python desktop app development. It contains all necessary scripts to build your final project, as well as code-sign them from Apple (Developer Account required).

## Currently supports
This currently supports (and has been tested on) Python 3.9.9 on MacOS 11.6. This tool may work on other systems, but has not been tested.
- Building .app files
- Signing .app files

## ToDo
- Building .pkg files
- Signing .pkg files
- Notorizing and Stapling .pkg files

# Setup
## Precursor - PyPi: PyMacApp
```pip3 install PyMacApp```
- Uses PyInstaller, should install automatically
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
### (2/2) Create an App-Specific password for altool to use
- Instructions from Apple to create: https://support.apple.com/en-us/HT204397
- Open KeyChain Access
- Create a "New Password Item"
- Keychain Item Name: Developer-altool
- Account Name: your developer account email
- Password: the application-specific password you just created

## Part 2: Get Your Hashes
### (1/3) Create Certificates with XCode
- Open XCode
- In the top-apple Menu, go to XCode > Preferences > Accounts > Your Account > In the team, chose the Admin team > Manage Certificates in the bottom-right
- click the plus in the bottom corner
- choose "Developer ID Application"
- repeating, click the plus in the bottom corner
- choose "Developer ID Installer"
### (2/3) Get Certificates and Add to Project
- run:
> security find-identity -p basic -v
- your output will look like:
> 1) HASH_OF_ID_HERE "Developer ID Application: ..."
> 2) HASH_OF_ID_HERE "Developer ID Installer: ..."
> 
>    2 valid identities found
- copy the appropriate hashes when using the Builder()
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
# Building & Packaging Your App
Use the Builder() and then call the .build_app(), .sign_app() functions. More coming soon. 
# Advanced Customization
## Pre- and Post-Install Scripting
Coming soon.
