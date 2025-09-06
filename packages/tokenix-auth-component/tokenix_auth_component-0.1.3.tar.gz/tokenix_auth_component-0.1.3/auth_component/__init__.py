"""
Tokenix Auth Component - Componente de autenticación reutilizable para lambdas de RapidCredit

Este paquete proporciona funcionalidades de autenticación HTTP para lambdas de RapidCredit
que requieran autenticarse en Tokenix, manejando el flujo de dos tokens: 
token de autenticación y token de API.
"""

__version__ = "0.1.3"
__author__ = "Edwin Caicedo Venté"
__email__ = "ecaicedo@rapicredit.com"

from .simple_auth import SimpleTokenixAuth, create_auth_client
from .exceptions import (
    AuthError,
    HTTPAuthError,
    InvalidCredentialsError,
    ServiceUnavailableError
)

__all__ = [
    "SimpleTokenixAuth",
    "create_auth_client",
    "AuthError",
    "HTTPAuthError",
    "InvalidCredentialsError",
    "ServiceUnavailableError",
]