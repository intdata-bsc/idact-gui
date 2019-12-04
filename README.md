[![Build Status - develop](https://travis-ci.com/intdata-bsc/idact-gui.svg?branch=develop)](https://travis-ci.com/intdata-bsc/idact-gui)

# Idact GUI

This is a graphical interface for the [idact](https://github.com/garstka/idact) project

## Getting Started

To install gui on your computer just run:

```
pip3 install idact-gui
``` 

Unfortunately pip doesn't support auto-installing dependencies from the external source. For gui to work you must also run the command installing the [idact form intdata-bsc](https://github.com/intdata-bsc/idact) repository.

```
pip3 install -e git+git://github.com/intdata-bsc/idact.git@<IDACT_VERSION>#egg=idact
```
The <IDACT_VERSION> shoud be corresponding to the version of gui you want to install. You can check the latest one [here](https://github.com/intdata-bsc/idact-gui/wiki).

After this small setup just run this command in terminal:

```
idactgui
```

## Dev build

After clonning the repository, inside `idact-gui` folder just run:

```
python -m gui.main
```

### Prerequisites

All requirements are listed in `requirements-dev.txt`. To install them run:

```
pip install -r requirements-dev.txt
```

The project depends on the [forked idact repository](https://github.com/intdata-bsc/idact) `develop` branch.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Wiki

Please visit our [wiki](https://github.com/intdata-bsc/idact-gui/wiki) where you can find FAQ and user documentation.
