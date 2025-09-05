# Expondo classes principais do SDK
from .Autorizacao_fontes import Autorizacao
from .Fonte_dados import Fonte_dados

__all__ = ["Fonte_dados", "Autorizacao"]

# versão da SDK (sincronize com pyproject.toml)
__version__ = "0.1.0"