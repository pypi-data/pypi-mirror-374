from .api import Robot
from .rubino import Bot
from .exceptions import APIRequestError
from .rubino import Bot as rubino

__all__ = [
    "Robot",
    "on_message",
    "APIRequestError",
    "create_simple_keyboard",
]