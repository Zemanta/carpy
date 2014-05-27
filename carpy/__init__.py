__all__ = ['wrapper', 'config']

from . import wrapper
from .config import Config

config = Config()
config.from_envvar('CARPY_CONFIG_FILE', silent=True)

