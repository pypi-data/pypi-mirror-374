"""
Cliente simple de autenticación para RapidCredit API
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

from .exceptions import AuthError, HTTPAuthError, InvalidCredentialsError, ServiceUnavailableError

# Cargar variables de entorno
load_dotenv()


class SimpleTokenixAuth:
    """
    Cliente simple de autenticación para Tokenix API.
    
    Maneja el flujo de dos endpoints:
    1. POST /v2/authorization/login -> obtiene token
    2. POST /v2/user/login -> obtiene accessToken
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializa el cliente de autenticación.
        
        Args:
            base_url: URL base de la API (por defecto desde env BASE_URL)
        """
        self.base_url = base_url or os.getenv('BASE_URL', 'https://demo-saas-rapicredit-api.token-city.com')
        
        # URLs de los endpoints
        self.auth_url = f"{self.base_url}/v2/authorization/login"
        self.user_url = f"{self.base_url}/v2/user/login"
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def get_access_token(
        self,
        api_key: str,
        email_auth: str,
        password_auth: str,
        email_user: str,
        password_user: str
    ) -> str:
        """
        Obtiene el accessToken completo siguiendo el flujo de dos endpoints.
        
        Args:
            api_key: API Key para las llamadas
            email_auth: Email para el primer endpoint
            password_auth: Password para el primer endpoint
            email_user: Email para el segundo endpoint
            password_user: Password para el segundo endpoint
        
        Returns:
            accessToken listo para usar
            
        Raises:
            AuthError: Si hay algún error en el proceso de autenticación
        """
        try:
            # Paso 1: Obtener token del primer endpoint
            auth_token = self._get_auth_token(api_key, email_auth, password_auth)
            
            # Paso 2: Obtener accessToken del segundo endpoint
            access_token = self._get_user_token(api_key, auth_token, email_user, password_user)
            
            return access_token
            
        except Exception as e:
            raise AuthError(f"Error obteniendo accessToken: {e}")
    
    def _get_auth_token(self, api_key: str, email_auth: str, password_auth: str) -> str:
        """
        Primer endpoint: POST /v2/authorization/login
        
        Args:
            api_key: API Key para las llamadas
            email_auth: Email para autenticación
            password_auth: Password para autenticación
        
        Returns:
            Token de autenticación
            
        Raises:
            HTTPAuthError: Si hay error en la llamada HTTP
            InvalidCredentialsError: Si las credenciales son inválidas
        """
        try:
            # Headers para el primer endpoint
            headers = {
                'Content-Type': 'application/json',
                'X-API-KEY': api_key
            }
            
            # Datos para el primer endpoint
            auth_data = {
                "email": email_auth,
                "password": password_auth
            }
            
            # Realizar llamada al primer endpoint
            response = self.session.post(self.auth_url, headers=headers, json=auth_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Verificar si hay error en la respuesta
                if 'error' in response_data:
                    raise InvalidCredentialsError(f"Error de autorización: {response_data['error']}")
                
                token = response_data.get('token')
                
                if not token:
                    raise HTTPAuthError("No se encontró token en la respuesta del primer endpoint")
                
                return token
                
            elif response.status_code == 401:
                raise InvalidCredentialsError("Credenciales inválidas para el primer endpoint")
            else:
                raise HTTPAuthError(
                    f"Error en primer endpoint: {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
                
        except requests.exceptions.RequestException as e:
            raise ServiceUnavailableError(f"Error de conexión en primer endpoint: {e}")
        except (InvalidCredentialsError, HTTPAuthError, ServiceUnavailableError):
            # Re-lanzar excepciones específicas
            raise
        except Exception as e:
            raise HTTPAuthError(f"Error inesperado en primer endpoint: {e}")
    
    def _get_user_token(self, api_key: str, auth_token: str, email_user: str, password_user: str) -> str:
        """
        Segundo endpoint: POST /v2/user/login
        
        Args:
            api_key: API Key para las llamadas
            auth_token: Token obtenido del primer endpoint
            email_user: Email para el segundo endpoint
            password_user: Password para el segundo endpoint
            
        Returns:
            accessToken de la API
            
        Raises:
            HTTPAuthError: Si hay error en la llamada HTTP
            InvalidCredentialsError: Si las credenciales son inválidas
        """
        try:
            # Headers para el segundo endpoint
            headers = {
                'X-ACCESS-TOKEN': auth_token,
                'Content-Type': 'application/json',
                'X-API-KEY': api_key
            }
            
            # Datos para el segundo endpoint
            user_data = {
                "email": email_user,
                "password": password_user,
                "secret": True
            }
            
            # Realizar llamada al segundo endpoint
            response = self.session.post(self.user_url, headers=headers, json=user_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Verificar que la respuesta sea exitosa
                if not response_data.get('status'):
                    raise HTTPAuthError(f"Error en respuesta del segundo endpoint: {response_data.get('message', 'Error desconocido')}")
                
                # Extraer accessToken
                data = response_data.get('data', {})
                access_token = data.get('accessToken')
                
                if not access_token:
                    raise HTTPAuthError("No se encontró accessToken en la respuesta del segundo endpoint")
                
                return access_token
                
            elif response.status_code == 401:
                raise InvalidCredentialsError("Credenciales inválidas para el segundo endpoint")
            else:
                raise HTTPAuthError(
                    f"Error en segundo endpoint: {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
                
        except requests.exceptions.RequestException as e:
            raise ServiceUnavailableError(f"Error de conexión en segundo endpoint: {e}")
        except Exception as e:
            raise HTTPAuthError(f"Error inesperado en segundo endpoint: {e}")
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        api_key: str,
        email_auth: str,
        password_auth: str,
        email_user: str,
        password_user: str,
        data: dict = None,
        params: dict = None,
        additional_headers: dict = None
    ) -> requests.Response:
        """
        Realiza una petición autenticada a la API de Tokenix.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, etc.)
            endpoint: Endpoint de la API (ej: "/v2/loans")
            api_key: API Key para las llamadas
            email_auth: Email para el primer endpoint
            password_auth: Password para el primer endpoint
            email_user: Email para el segundo endpoint
            password_user: Password para el segundo endpoint
            data: Datos a enviar en el cuerpo
            params: Parámetros de consulta
            additional_headers: Headers adicionales (ej: {"X-USER-ACCESS-TOKEN": "token"})
            
        Returns:
            Respuesta HTTP
            
        Raises:
            AuthError: Si hay algún error en la petición
        """
        try:
            # Obtener accessToken
            access_token = self.get_access_token(
                api_key, email_auth, password_auth, email_user, password_user
            )
            
            # Construir URL completa
            url = f"{self.base_url}{endpoint}"
            
            # Headers con accessToken (mantener los originales)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Agregar headers adicionales si se proporcionan
            if additional_headers:
                headers.update(additional_headers)
            
            # Realizar petición
            return self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
        except Exception as e:
            raise AuthError(f"Error en petición a Tokenix: {e}")
    
    def close(self):
        """Cierra la sesión HTTP."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Función de conveniencia
def create_auth_client(base_url: Optional[str] = None) -> SimpleTokenixAuth:
    """
    Función de conveniencia para crear un cliente de autenticación.
    
    Args:
        base_url: URL base de la API (opcional, usa variable de entorno por defecto)
        
    Returns:
        Cliente de autenticación para Tokenix
    """
    return SimpleTokenixAuth(base_url=base_url)
