from setuptools import setup, find_packages
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="CTpackage",
    version="0.1.1",
    description="This my first package. Can use to calculate area, length of circle and area of a sector of a circle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="THITIRAT",
    author_email="thitirat98242@gmail.com",
    url="https://github.com/Cartoonmee/CTpackage",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)

