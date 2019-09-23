import json


class NativeArgsSaver:
    def __init__(self):
        self.filename = 'native_args.json'
        with open(self.filename) as json_file:
            self.native_list = json.load(json_file)

    def save(self, native_list):
        self.native_list = native_list
        with open(self.filename, 'w') as json_file:
            json.dump(native_list, json_file)

    def get_native_args_list(self):
        return self.native_list

    def add_to_list(self, new_args):
        self.native_list.append(new_args)
        self.save(self.native_list)

    def remove_native_arg(self, name):
        name = '--' + name
        new_list = [item for item in self.native_list if item[0] != name]
        self.native_list = new_list
        self.save(self.native_list)

