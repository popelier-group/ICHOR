class Modules(dict):
    def __getitem__(self, item) -> list:
        if item not in self.keys():
            return []
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        if key in self.keys():
            self[key] += value
        else:
            super().__setitem__(key, value)
