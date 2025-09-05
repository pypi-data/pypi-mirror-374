from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  # mantém 'matrix' como namespace compartilhado

# Atalho público:
from .zion import Zion
__all__ = ["Zion"]