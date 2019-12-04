""" One of the helpers for the gui application.

    Similar modules: class:`.NativeArgsSaver`, :class:`.ParameterSaver`,
    :class:`.UiLoader`, :class:`.Worker`, :class:`.DataProvider`
"""
from pathlib import Path
import os.path
from shutil import copyfile
from idact.detail.environment.environment_impl import EnvironmentImpl
from idact.detail.environment.environment_text_serialization import \
    serialize_environment


class ConfigurationProvider:
    """ Provides the configuration for idact if it doesn't exist.
    """

    def __init__(self):
        self.filepath = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = 'assets'

        self.filename = ".idact.conf"
        self.home_path = str(Path.home())
        self.conf_file_path = os.path.join(self.home_path, self.filename)

        self.filename_args = "args.json"
        self.clean_args_file_path = os.path.join(self.filepath, self.assets_dir, self.filename_args)
        self.args_file_path = os.path.join(self.filepath, os.pardir, os.pardir, self.filename_args)

        self.filename_native_args = "native_args.json"
        self.clean_native_args_file_path = os.path.join(self.filepath, self.assets_dir, self.filename_native_args)
        self.native_args_file_path = os.path.join(self.filepath, os.pardir, os.pardir, self.filename_native_args)

    def create_conf_file(self):
        """ Creates the config file.
        """
        environment_impl = EnvironmentImpl()
        with open(self.conf_file_path, 'w') as file:
            file.write(serialize_environment(environment_impl))

    def check_if_conf_file_exists(self):
        return os.path.exists(self.conf_file_path)

    def create_args_files(self):
        """ Creates the args file.
        """
        copyfile(self.clean_args_file_path, self.args_file_path)
        copyfile(self.clean_native_args_file_path, self.native_args_file_path)

    def check_if_args_files_exist(self):
        return os.path.exists(self.args_file_path) and os.path.exists(self.native_args_file_path)
