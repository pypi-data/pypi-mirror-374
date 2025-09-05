"""
Excepciones para el componente de autenticación HTTP
"""


class AuthError(Exception):
    """Excepción base para errores de autenticación"""
    pass


class HTTPAuthError(AuthError):
    """Excepción lanzada cuando hay errores en las llamadas HTTP de autenticación"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class InvalidCredentialsError(AuthError):
    """Excepción lanzada cuando las credenciales son inválidas"""
    pass


class ServiceUnavailableError(AuthError):
    """Excepción lanzada cuando el servicio de autenticación no está disponible"""
    pass
