from setuptools import setup, find_packages

setup(
    name="museum_security",
    version="0.1",
    packages=find_packages(),
    description="Museum Security Project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sainoonlh/museum_security",
    author="Sai Noom",
    author_email="sainoonlengharn@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
