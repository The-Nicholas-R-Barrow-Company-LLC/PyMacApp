import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyMacApp",
    version="0.0.1",
    author="The Nicholas R. Barrow Company, LLC",
    author_email="me@nicholasrbarrow.com",
    description="A boilerplate for creating MacOS desktop apps and installers, including signing and notorizing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp",
    project_urls={
        "Bug Tracker": "https://github.com/The-Nicholas-R-Barrow-Company-LLC/PyMacApp/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "boilerplate"},
    packages=setuptools.find_packages(where="boilerplate"),
    python_requires=">=3.9",
    install_requires=["PyInstaller"]
)