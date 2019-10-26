import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="idact-gui",
    version="0.0.1",
    author="Joanna Chyży, Karolina Piekarz, Piotr Swędrak",
    author_email="piotrekswedrak@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intdata-bsc/idact-gui",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'idact'
    ],
    entry_points={
        'console_scripts': [
            'idactgui=gui.main:start',
        ],
    }
)
