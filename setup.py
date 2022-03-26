import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="PyMacApp",
    version="1.2.3",
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
    packages=["pymacapp"],
    include_package_data=True,
    install_requires=["PyInstaller"],
    project_urls={
        'Source': 'https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp',
        'Tracker': 'https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp/issues',
    }
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
)