"""Base api class"""


class Api:

    def get(self, path, params=None, json=None, ignore_json=False):
        raise NotImplementedError()
