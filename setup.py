import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvbcc",
    version="0.0.1",
    author="Peter Bartha",
    author_email="peitur@gmail.com",
    description="Small experimental VBox tool to manage VBox machines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/peitur/pyvbcc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)