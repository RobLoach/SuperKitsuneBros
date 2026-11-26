"""where things are: the repository, the downloaded nesmaps images and this folder"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NES = os.environ.get('NESMAPS', os.path.join(HERE, 'nesmaps'))
