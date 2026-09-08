from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

# --- AUTH SCHEMAS ---
class LoginRequest(BaseModel):
    login_id: str  # Puede ser CI o Correo Electrónico
    password: str
    remember_me: Optional[bool] = False

class ForgotPasswordRequest(BaseModel):
    login_id: str  # CI o Correo Electrónico

class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str
    ci: str

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

# --- BITACORA SCHEMAS ---
class BitacoraCreate(BaseModel):
    id_usuario: Optional[str] = None
    accion_realizada: str
    tabla_afectada: Optional[str] = None

class BitacoraOut(BaseModel):
    id_bitacora: int
    id_usuario: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    accion_realizada: str
    tabla_afectada: Optional[str] = None
    usuario_nombre: Optional[str] = None
    usuario_rol: Optional[str] = None

    class Config:
        from_attributes = True

# --- USUARIO SCHEMAS ---
class UsuarioBase(BaseModel):
    ci: str
    nombre: str
    rol: str

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioOut(UsuarioBase):
    class Config:
        from_attributes = True

# --- CLIENTE REGISTER SCHEMA ---
class ClienteRegister(BaseModel):
    ci: str
    nombre: str
    apellido: str
    genero: Optional[str] = "No especificado"
    correo_electronico: EmailStr
    telefono: Optional[str] = ""
    edad: Optional[int] = 18
    contrasena: str

# --- TOKEN SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class TokenData(BaseModel):
    ci: Optional[str] = None
    rol: Optional[str] = None
