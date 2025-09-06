from __future__ import annotations
import pygame
from typing import Tuple
import os

_screen = None

# Path to the default icon inside your package
_default_icon_path = os.path.join(os.path.dirname(__file__), "assets", "pylove_icon.png")
_default_icon = pygame.image.load(_default_icon_path)


def _init_window(width: int, height: int, title: str):
    """Initialize the main window with default icon."""
    global _screen
    _screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(title)
    pygame.display.set_icon(_default_icon)  # Use default icon automatically


def _get_screen():
    return _screen


def set_title(title: str):
    pygame.display.set_caption(title)


def set_fullscreen(enabled: bool = True):
    flags = pygame.FULLSCREEN if enabled else pygame.RESIZABLE
    size = _screen.get_size()
    pygame.display.set_mode(size, flags)


def get_size() -> Tuple[int, int]:
    return _screen.get_size()


def set_icon(path: str = None):
    """
    Set a custom window icon.
    If no path is provided, the default PyLove2D icon is used.
    """
    if path is None:
        surf = _default_icon
    else:
        surf = pygame.image.load(path)
    pygame.display.set_icon(surf)
