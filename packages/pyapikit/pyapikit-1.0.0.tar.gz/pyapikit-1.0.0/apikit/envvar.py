# coding: utf-8

import os

class EnvVar:
    def __init__(self, name: str, default: str = None):
        self.name = name
        self.default = default

    def __get__(self, obj, objtype):
        return os.getenv(self.name, self.default)
    