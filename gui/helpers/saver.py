import json


class ParameterSaver:
    def __init__(self):
        self.filename = 'args.json'
        with open(self.filename) as json_file:
            self.data = json.load(json_file)

    def save(self, data):
        self.data = data
        with open(self.filename, 'w') as json_file:
            json.dump(data, json_file)
            
    def get_map(self):
        return self.data
