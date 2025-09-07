from .client import TelegramClient 
from ..extra import ExtraFeatures
from .auth import AuthMethods

class TeloxiClient(AuthMethods,ExtraFeatures,TelegramClient):
    pass


__all__ = ['TeloxiClient']


