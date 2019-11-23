""" One of the helpers for the gui application.

    Similar modules: class:`.DataProvider`, :class:`.ParameterSaver`,
    :class:`.UiLoader`, :class:`.Worker`, :class:`.ConfigurationProvider`
"""
import json
import os


class NativeArgsSaver:
    """ Manages the native arguments.
    """

    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(current_directory, '../../native_args.json')
        with open(self.filename) as json_file:
            self.native_args = json.load(json_file)

    def save(self, native_args):
        """ Saves the native arguments into a json file.

            :param native_args: Native arguments to be saved.
        """
        self.native_args = native_args
        with open(self.filename, 'w') as json_file:
            json.dump(native_args, json_file)

    def get_native_args(self):
        return self.native_args
