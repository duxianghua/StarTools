import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from saltfish.script import game_service


if __name__ == '__main__':
    game_service()