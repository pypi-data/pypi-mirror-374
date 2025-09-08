from setuptools import setup, find_packages

setup(
    name="lambda-universal-router",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    author="Raumil Dhandhukia",
    author_email="raumild@gmail.com",
    description="A flexible AWS Lambda event router with support for multiple event sources",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/raumildhandhukia/lambda-universal-router",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
