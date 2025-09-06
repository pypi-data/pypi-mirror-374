# Tokenix Auth Component

Componente de autenticación reutilizable para lambdas de RapidCredit que requieran autenticarse en Tokenix.

## Instalación

```bash
pip install tokenix-auth-component
```

### Dependencias

El paquete requiere las siguientes dependencias (se instalan automáticamente):
- `requests>=2.25.0` - Para peticiones HTTP
- `python-dotenv>=0.19.0` - Para variables de entorno (opcional)

## Uso

### Importar el cliente

```python
from auth_component import create_auth_client
```

### Obtener accessToken

```python
# Crear cliente
auth_client = create_auth_client()

# Obtener accessToken
access_token = auth_client.get_access_token(
    api_key="tu-api-key",
    email_auth="email-para-primer-endpoint",
    password_auth="password-para-primer-endpoint", 
    email_user="email-para-segundo-endpoint",
    password_user="password-para-segundo-endpoint"
)
```

### Realizar peticiones autenticadas

```python
# Realizar petición HTTP autenticada
response = auth_client.make_request(
    method="GET",  # o "POST", "PUT", "DELETE"
    endpoint="/v2/user/profile",
    api_key="tu-api-key",
    email_auth="email-para-primer-endpoint",
    password_auth="password-para-primer-endpoint",
    email_user="email-para-segundo-endpoint", 
    password_user="password-para-segundo-endpoint",
    data={"key": "value"},  # opcional para POST/PUT
    params={"param": "value"}  # opcional para query parameters
)
```

### Uso con context manager

```python
with create_auth_client() as auth_client:
    access_token = auth_client.get_access_token(**credentials)
    response = auth_client.make_request("GET", "/v2/endpoint", **credentials)
```

## Variables de Entrada

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `api_key` | Clave API de Tokenix | `"xxx-xxx-xxxx"` |
| `email_auth` | Email para primer endpoint de autenticación | `"user+api@token-city.com"` |
| `password_auth` | Password para primer endpoint de autenticación | `"password123"` |
| `email_user` | Email para segundo endpoint de autenticación | `"user-manager@token-city.com"` |
| `password_user` | Password para segundo endpoint de autenticación | `"managerPassword123"` |

## Manejo de Errores

El paquete incluye manejo de errores específicos:

```python
from auth_component import AuthError, InvalidCredentialsError, ServiceUnavailableError

try:
    access_token = auth_client.get_access_token(**credentials)
except InvalidCredentialsError:
    print("Credenciales inválidas")
except ServiceUnavailableError:
    print("Servicio no disponible")
except AuthError:
    print("Error de autenticación general")
```

## Ejemplo Completo

```python
from auth_component import create_auth_client

# Credenciales
credentials = {
    "api_key": "tu-api-key",
    "email_auth": "email-auth@token-city.com",
    "password_auth": "password-auth",
    "email_user": "email-user@token-city.com", 
    "password_user": "password-user"
}

# Usar cliente
with create_auth_client() as auth_client:
    # Obtener token
    token = auth_client.get_access_token(**credentials)
    print(f"Token: {token}")
    
    # Hacer petición
    response = auth_client.make_request("GET", "/v2/user/profile", **credentials)
    print(f"Status: {response.status_code}")
    print(f"Data: {response.json()}")
```

## Pruebas

Para probar el paquete localmente:

1. **Copia el archivo de ejemplo:**
   ```bash
   cp test_auth.py.example test_auth.py
   ```

2. **Edita las credenciales en `test_auth.py`:**
   - Reemplaza las credenciales de ejemplo con las reales
   - **NO subas `test_auth.py` con credenciales reales a PyPI**

3. **Ejecuta las pruebas:**
   ```bash
   python3 test_auth.py
   ```

**⚠️ Importante:** El archivo `test_auth.py` con credenciales reales debe mantenerse local y no subirse a repositorios públicos.