from setuptools import setup, find_packages

setup(
    name="weblib-py",
    version="0.1.1",
    description="Una libreria Python semplice per creare webapp",
    author="Valerio",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "Flask>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
