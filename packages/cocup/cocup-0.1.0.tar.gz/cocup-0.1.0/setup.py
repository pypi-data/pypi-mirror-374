from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    description = fh.read()

setup(
    name="cocup",
    version="0.1.0",
    description="Thom's COokie CUtter for Python",
    long_description=description,
    long_description_content_type="text/markdown",
    author="Thomas J. Booth",
    author_email="thoboo@biosustain.dtu.dk",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "cocup": ["templates/**/*"],
    },           
    install_requires=[],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "cocup=cocup.main:main",
        ],
    },
)
