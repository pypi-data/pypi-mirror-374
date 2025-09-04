from setuptools import setup, find_packages
import os

def parse_requirements(filename):
    """Read requirements from file, removing comments and empty lines"""
    requirements = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements
path = os.path.join(os.getenv('BUILD_PATH'), "requirements.txt")
setup(
    name="rule-engine-core",  
    version="0.0.2",          
    author="Mohit Tripathi",     
    author_email="tripathimohit051@gmail.com",
    description="A rule engine core library for Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/temp-noob/rule-engine", 
    packages=find_packages(),  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  
    # install_requires=parse_requirements("/home/tripathimohit051/rule-engine/rule-engine-core/requirements.txt")
    install_requires=parse_requirements(path),  # Use the function to parse requirements
)