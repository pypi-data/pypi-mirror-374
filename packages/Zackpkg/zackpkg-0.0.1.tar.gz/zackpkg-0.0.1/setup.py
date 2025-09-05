from setuptools import setup , find_packages
import codecs
import os 

VERSION = '0.0.1'
DESCRIPTION = 'library to print hello in my package'
LONG_DESCRIPTION = 'A package that allows to build simple streams video'

# Setting up 
setup(
    name="Zackpkg" , 
    version=VERSION , 
    author="ArabCodeX", 
    author_email="zakaria.ahmed6765@gmail.com", 
    description=DESCRIPTION,
    long_description_content_type= "text/markdown", 
    long_description=LONG_DESCRIPTION, 
    packages=find_packages(),
    install_requires = [],
    keywords=['python' , 'Zack' , 'Hello'],
    classifiers=[
    "Development Status :: 1 - Planning", 
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3", 
    "Operating System :: Unix",
    "Operating System :: MacOS :: MacOS X", 
    "Operating System :: Microsoft :: Windows", 
]
   
)