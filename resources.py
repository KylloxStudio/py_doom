import os
import sys

class Resources:
    @staticmethod
    def get_path(relative_path):
        if sys.platform == 'emscripten': return relative_path
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)