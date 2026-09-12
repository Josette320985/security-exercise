import os
import time

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ldap3 import Server, Connection, ALL

app = FastAPI(
    title="LDAP Authentication API",
    description="Educational FastAPI + OpenLDAP example with secret rotation",
    version="1.0.0",
)

# Permitir CORS para que el frontend pueda llamar directamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LDAP_HOST = os.getenv("LDAP_HOST", "openldap")
LDAP_PORT = int(os.getenv("LDAP_PORT", "389"))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "dc=example,dc=com")
LDAP_ADMIN_PASSWORD = os.getenv("LDAP_ADMIN_PASSWORD", "adminpassword")

# Ruta al archivo de secretos compartido
SECRET_FILE = "/app/.secret"
SHARED_SECRET_FILE = "/shared-html/.ldap-secret"


def get_current_api_key() -> str:
    """Lee la API key actual desde el archivo de rotación o la variable de entorno."""
    try:
        with open(SECRET_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.getenv("LDAP_API_KEY", "ldap-secret-initial-key")


def validate_api_key(x_api_key: str = Header(None)) -> bool:
    """Valida que el header x-api-key coincida con el secreto actual."""
    current = get_current_api_key()
    if x_api_key != current:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing API key",
        )
    return True


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(request: LoginRequest):
    """
    Autentica un usuario contra OpenLDAP.
    Endpoint protegido: requiere header x-api-key.
    """
    # Nota: el login lo dejamos accesible desde el frontend.
    # Si quieres protegerlo, descomenta la siguiente línea:
    # validate_api_key(x_api_key)

    server = Server(LDAP_HOST, port=LDAP_PORT, get_info=ALL)

    user_dn = f"uid={request.username},ou=users,{LDAP_BASE_DN}"

    connection = Connection(
        server,
        user=user_dn,
        password=request.password,
        auto_bind=False,
    )

    try:
        if connection.bind():
            return {
                "authenticated": True,
                "username": request.username,
                "dn": user_dn,
            }
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
    finally:
        connection.unbind()


@app.get("/api/verify-key")
def verify_key(x_api_key: str = Header(None)):
    """Endpoint para que el frontend verifique si su API key es válida."""
    validate_api_key(x_api_key)
    return {"valid": True, "message": "API key is valid"}