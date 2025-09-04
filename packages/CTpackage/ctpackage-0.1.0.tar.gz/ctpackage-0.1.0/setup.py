from setuptools import setup, find_packages

setup(
    name="CTpackage",               # Must be unique on PyPI!
    version="0.1.0",                # Follow semantic versioning
    description="This my frist package. Can ues to calulate area length circle",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Cartoon",
    author_email="your_email@example.com",
    url="https://github.com/Cartoonmee/CTpackage",  # optional
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)