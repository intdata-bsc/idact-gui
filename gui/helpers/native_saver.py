import json


class NativeArgsSaver:
    def __init__(self):
        self.filename = 'native_args.json'
        with open(self.filename) as json_file:
            self.native_args = json.load(json_file)

    def save(self, native_args):
        self.native_args = native_args
        with open(self.filename, 'w') as json_file:
            json.dump(native_args, json_file)

    def get_native_args(self):
        return self.native_args

    def clear(self):
        self.native_args = []
        self.save(self.native_args)

