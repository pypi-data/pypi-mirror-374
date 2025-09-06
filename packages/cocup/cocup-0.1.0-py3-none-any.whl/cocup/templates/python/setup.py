from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    description = fh.read()

setup(
    name="{project_name}",
    version="0.0.1",
    description="{description}",
    long_description=description,
    long_description_content_type="text/markdown",
    author="{author}",
    author_email="{email}",
    packages=find_packages(),
    install_requires=[
        {requirements}
        ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "{project_name}={project_name}.main:main",
        ],
    },
)

