""" One of the helpers for the gui application.

    Similar modules: class:`.NativeArgsSaver`, :class:`.ParameterSaver`,
    :class:`.UiLoader`, :class:`.Worker`, :class:`.DataProvider`
"""
from pathlib import Path
import os.path
from idact.detail.environment.environment_impl import EnvironmentImpl
from idact.detail.environment.environment_text_serialization import \
    serialize_environment


class ConfigurationProvider:
    """ Provides the configuration for idact if it doesn't exist.
    """

    def __init__(self):
        self.filename = ".idact.conf"
        self.home_path = str(Path.home())
        self.conf_file_path = os.path.join(self.home_path, self.filename)

    def create_conf_file(self):
        """ Creates the config file.
        """
        environment_impl = EnvironmentImpl()
        with open(self.conf_file_path, 'w') as file:
            file.write(serialize_environment(environment_impl))

    def check_if_conf_file_exists(self):
        return os.path.exists(self.conf_file_path)