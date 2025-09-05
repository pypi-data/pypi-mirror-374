from setuptools import setup, find_packages

setup(
    name="gits",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        "clight",
        "colored"
    ],
    entry_points={
        "console_scripts": [
            "gits=gits.main:main",  # Entry point of the app
        ],
    },
    package_data={
        "gits": [
            "main.py",
            "__init__.py",
            ".system/imports.py",
            ".system/index.py",
            ".system/modules/gitssh.py",
            ".system/sources/clight.json",
            ".system/sources/logo.ico",
            ".system/sources/sshconfig"
        ],
    },
    include_package_data=True,
    author="Irakli Gzirishvili",
    author_email="gziraklirex@gmail.com",
    description="Gits is a Python command-line application designed to help you to handle multiple GitHub and GitLab repositories on your machine. With using Gits, you can start cloning from and pushing to multiple GitHub and GitLab accounts without any additional configurations - It automatically sets up everything needed to prevent conflicts between your accounts.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IG-onGit/Gits",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
