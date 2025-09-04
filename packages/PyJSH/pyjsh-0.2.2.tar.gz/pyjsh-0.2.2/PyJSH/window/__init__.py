#project2/PyJSH/window/__init__.py
from .open import *
from .figure import *
from .color import *
from os import environ
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from pygame import *