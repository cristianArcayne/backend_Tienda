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

class UsuarioCreateFull(BaseModel):
    ci: str
    nombre: str
    rol: str  # 'administrador', 'empleado' / 'trabajador', 'cliente'
    contrasena: str
    # Campos opcionales para cliente
    apellido: Optional[str] = ""
    genero: Optional[str] = "No especificado"
    correo_electronico: Optional[str] = None
    telefono: Optional[str] = ""
    edad: Optional[int] = 18
    # Campos opcionales para empleado
    id_sucursal: Optional[int] = None

class UsuarioDetailOut(BaseModel):
    ci: str
    nombre: str
    rol: str
    # Datos de cliente
    apellido: Optional[str] = None
    correo_electronico: Optional[str] = None
    telefono: Optional[str] = None
    genero: Optional[str] = None
    edad: Optional[int] = None
    # Datos de empleado
    id_sucursal: Optional[int] = None
    sucursal_nombre: Optional[str] = None

    class Config:
        from_attributes = True

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

# --- EMPRESA / CONFIGURACION ---
class EmpresaConfig(BaseModel):
    razon_social: str = "TPV Minimarket Demo S.A.C."
    nombre_comercial: str = "Mi Minimarket"
    ruc_nit: str = "20100100100"
    direccion: str = "Av. Principal 123"
    ciudad: str = "Lima"
    telefono: str = "01-555-1234"
    email: str = "contacto@minimarket.com"
    sitio_web: str = "www.minimarket.com"
    simbolo_moneda: str = "$"
    codigo_moneda: str = "Dólar (USD)"
    iva_porcentaje: float = 18.0
    precios_con_impuesto: bool = True
