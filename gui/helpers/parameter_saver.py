""" One of the helpers for the gui application.

    Similar modules: class:`.DataProvider`, :class:`.NativeArgsSaver`,
    :class:`.UiLoader`, :class:`.Worker`, :class:`.ConfigurationProvider`
"""
import json
import os


class ParameterSaver:
    """ Manages the gui arguments.
    """

    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(current_directory, '../../args.json')
        with open(self.filename) as json_file:
            self.data = json.load(json_file)

    def save(self, data):
        """ Saves the gui arguments into a json file.

            :param data: Gui arguments to be saved.
        """
        self.data = data
        with open(self.filename, 'w') as json_file:
            json.dump(data, json_file)

    def get_map(self):
        return self.data
