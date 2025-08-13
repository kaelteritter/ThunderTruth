import os
import sys


def get_path_compiling(filepath: str):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, filepath)