import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "wr_toolkit",
    version = "0.0.1",
    author = "WebRiders",
    author_email = "contact@webriders.com.ua",
    description = ("An demonstration of how to create, document, and publish "
                   "to the cheese shop a5 pypi.org."),
    license = "MIT",
    keywords = "django toolkit utilities",
    url = "https://github.com/webriders/wr-toolkit",
    packages=['wr_toolkit'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        ],
)