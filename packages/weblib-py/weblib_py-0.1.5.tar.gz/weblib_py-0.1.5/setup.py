from setuptools import setup, find_packages

setup(
    name="weblib-py",  # o il nuovo nome che scegli
    version="0.1.5",
    author="Valerio Domenici",
    author_email="valeriodomenici93@gmail.com",
    description="The Python library that revolutionizes web development",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Valerio357/weblib",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
)