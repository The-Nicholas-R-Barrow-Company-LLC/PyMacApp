import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
__version__ = "2.0.8"

setup(
    name="PyMacApp",
    version=__version__,
    description="Basic Tools to Build, Package, Sign, and Notorize Python Apps for MacOS",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp",
    author="The Nicholas R. Barrow Company, LLC",
    author_email="me@nicholasrbarrow.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["pymacapp", "pymacapp.app", "pymacapp.package"],
    package_data={'pymacapp': ['entitlements.plist']},
    include_package_data=True,
    install_requires=["PyInstaller"],
    project_urls={
        'Source': 'https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp',
        'Tracker': 'https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp/issues',
    }
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
)