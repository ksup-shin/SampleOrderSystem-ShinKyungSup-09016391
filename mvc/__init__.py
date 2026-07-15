"""
mvc - A minimal, reusable Model-View-Controller skeleton for CUI (Console UI) applications.

Import this package into any project to build MVC-structured console apps:

    from mvc import Model, View, Controller, Application

Design notes:
- Model: holds state, knows nothing about View/Controller. Notifies observers on change.
- View: renders to / reads from the console only. Knows nothing about Model internals.
- Controller: wires user input (from View) to Model mutations, and Model changes to View renders.
- Application: the glue that owns one Model/View/Controller triple and runs the main loop.
"""

from .model import Model
from .view import View
from .controller import Controller
from .app import Application

__all__ = ["Model", "View", "Controller", "Application"]

__version__ = "0.1.0"
