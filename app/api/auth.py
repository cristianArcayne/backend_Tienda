from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.models import Usuario, Cliente, Empleado, Administrador
from app.schemas.schemas import (
    LoginRequest, 
    Token, 
    ClienteRegister, 
    ForgotPasswordRequest, 
    ForgotPasswordResponse, 
    ResetPasswordRequest,
    UsuarioOut
)
from app.services.bitacora_service import registrar_bitacora

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def find_usuario_by_login_id(db: Session, login_id: str) -> tuple[Usuario | None, str | None]:
    """Busca al usuario por CI, Nombre o Correo Electrónico (si es cliente)."""
    clean_id = login_id.strip()
    
    # 1. Búsqueda directa por CI
    user = db.query(Usuario).filter(Usuario.ci == clean_id).first()
    if user:
        correo = user.cliente.correo_electronico if user.cliente else None
        return user, correo

    # 2. Búsqueda por correo electrónico en tabla cliente
    cliente = db.query(Cliente).filter(Cliente.correo_electronico.ilike(clean_id)).first()
    if cliente and cliente.usuario:
        return cliente.usuario, cliente.correo_electronico

    # 3. Búsqueda por nombre de usuario
    user_by_name = db.query(Usuario).filter(Usuario.nombre.ilike(clean_id)).first()
    if user_by_name:
        correo = user_by_name.cliente.correo_electronico if user_by_name.cliente else None
        return user_by_name, correo

    return None, None

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """Inicia sesión validando credenciales y genera un token JWT."""
    usuario, email = find_usuario_by_login_id(db, login_data.login_id)
    
    if not usuario or not verify_password(login_data.password, usuario.contrasena):
        # Registrar intento fallido en bitácora
        registrar_bitacora(
            db=db,
            id_usuario=usuario.ci if usuario else None,
            accion_realizada=f"INICIO_SESION_FALLIDO: Intento con identificador '{login_data.login_id}'",
            tabla_afectada="usuario"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifique su identificador o contraseña."
        )

    # Duración del token (si seleccionó 'Recordar sesión' dura 7 días, sino 24 horas)
    expire_delta = timedelta(days=7) if login_data.remember_me else timedelta(hours=24)
    
    token_claims = {
        "nombre": usuario.nombre,
        "rol": usuario.rol
    }
    if email:
        token_claims["email"] = email

    access_token = create_access_token(
        subject=usuario.ci,
        expires_delta=expire_delta,
        claims=token_claims
    )

    # Registrar inicio exitoso en bitácora
    registrar_bitacora(
        db=db,
        id_usuario=usuario.ci,
        accion_realizada=f"INICIO_SESION_EXITOSO: Rol '{usuario.rol}'",
        tabla_afectada="usuario"
    )

    user_info = {
        "ci": usuario.ci,
        "nombre": usuario.nombre,
        "rol": usuario.rol,
        "email": email or f"{usuario.nombre.lower().replace(' ', '.')}@atelier.com"
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_info
    }

@router.post("/register", response_model=Token)
def register_cliente(data: ClienteRegister, db: Session = Depends(get_db)) -> Any:
    """Registra un nuevo cliente y su usuario correspondiente."""
    # Verificar si el CI ya existe
    if db.query(Usuario).filter(Usuario.ci == data.ci).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el CI {data.ci}."
        )

    # Verificar si el correo ya existe
    if db.query(Cliente).filter(Cliente.correo_electronico.ilike(data.correo_electronico)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con el correo {data.correo_electronico}."
        )

    hashed_pw = get_password_hash(data.contrasena)

    # Crear Usuario
    nuevo_usuario = Usuario(
        ci=data.ci,
        nombre=f"{data.nombre} {data.apellido}".strip(),
        contrasena=hashed_pw,
        rol="cliente"
    )
    db.add(nuevo_usuario)
    db.flush()

    # Crear Cliente
    nuevo_cliente = Cliente(
        ci=data.ci,
        apellido=data.apellido,
        genero=data.genero,
        correo_electronico=data.correo_electronico,
        telefono=data.telefono,
        edad=data.edad
    )
    db.add(nuevo_cliente)
    db.commit()

    # Registrar en bitácora
    registrar_bitacora(
        db=db,
        id_usuario=nuevo_usuario.ci,
        accion_realizada="REGISTRO_CLIENTE_EXITOSO",
        tabla_afectada="cliente"
    )

    # Auto-login generando token
    access_token = create_access_token(
        subject=nuevo_usuario.ci,
        claims={"nombre": nuevo_usuario.nombre, "rol": "cliente", "email": data.correo_electronico}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "ci": nuevo_usuario.ci,
            "nombre": nuevo_usuario.nombre,
            "rol": "cliente",
            "email": data.correo_electronico
        }
    }

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)) -> Any:
    """Inicia el proceso de recuperación de contraseña y genera un token temporal."""
    usuario, email = find_usuario_by_login_id(db, req.login_id)
    if not usuario:
        # Registrar intento de recuperación fallido
        registrar_bitacora(
            db=db,
            id_usuario=None,
            accion_realizada=f"RECUPERACION_FALLIDA: Identificador inexistente '{req.login_id}'",
            tabla_afectada="usuario"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna cuenta asociada a los datos proporcionados."
        )

    # Generar token temporal de reseteo con expiración de 15 minutos
    reset_token = create_access_token(
        subject=usuario.ci,
        expires_delta=timedelta(minutes=15),
        claims={"type": "password_reset", "ci": usuario.ci}
    )

    registrar_bitacora(
        db=db,
        id_usuario=usuario.ci,
        accion_realizada=f"RECUPERACION_SOLICITADA: Token emitido para {usuario.ci}",
        tabla_afectada="usuario"
    )

    return {
        "message": "Solicitud de recuperación procesada con éxito. Utilice el token para redefinir su contraseña.",
        "reset_token": reset_token,
        "ci": usuario.ci
    }

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)) -> Any:
    """Restablece la contraseña utilizando el token de recuperación."""
    payload = decode_token(req.reset_token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace o token de recuperación es inválido o ha expirado."
        )

    ci = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.ci == ci).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario asociado a este token ya no existe."
        )

    usuario.contrasena = get_password_hash(req.new_password)
    db.commit()

    registrar_bitacora(
        db=db,
        id_usuario=usuario.ci,
        accion_realizada="CONTRASENA_RESTABLECIDA_EXITOSAMENTE",
        tabla_afectada="usuario"
    )

    return {"message": "Contraseña actualizada exitosamente. Ya puede iniciar sesión con su nueva credencial."}

@router.get("/me")
def get_me(current_user: Usuario = Depends(get_current_user)) -> Any:
    """Retorna la información del usuario autenticado actualmente."""
    email = current_user.cliente.correo_electronico if current_user.cliente else None
    return {
        "ci": current_user.ci,
        "nombre": current_user.nombre,
        "rol": current_user.rol,
        "email": email or f"{current_user.nombre.lower().replace(' ', '.')}@atelier.com"
    }

@router.post("/guest-login", response_model=Token)
def guest_login(db: Session = Depends(get_db)) -> Any:
    """Genera una sesión de invitado temporal para explorar el catálogo de la tienda."""
    guest_ci = "INVITADO"
    access_token = create_access_token(
        subject=guest_ci,
        claims={"nombre": "Invitado", "rol": "invitado", "email": "invitado@minimarket.com"}
    )

    registrar_bitacora(
        db=db,
        id_usuario=None,
        accion_realizada="ACCESO_INVITADO: Exploración de catálogo sin credenciales",
        tabla_afectada="sistema"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "ci": guest_ci,
            "nombre": "Invitado",
            "rol": "invitado",
            "email": "invitado@minimarket.com"
        }
    }
