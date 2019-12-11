import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements-pip.txt') as requirements_file:
    REQUIREMENTS = [i for i in requirements_file.readlines() if i]

setuptools.setup(
    name="idact-gui",
    version="0.4.1",
    author="Joanna Chyży, Karolina Piekarz, Piotr Swędrak",
    author_email="piotrekswedrak@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intdata-bsc/idact-gui",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'idactgui=gui.main:main',
        ],
    }
)
