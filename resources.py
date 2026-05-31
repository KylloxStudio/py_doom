import os

class Resources:
    @staticmethod
    def get_path(relative_path):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)