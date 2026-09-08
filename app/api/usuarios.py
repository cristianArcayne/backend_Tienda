from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.models.models import Usuario, Administrador, Empleado, Cliente
from app.schemas.schemas import UsuarioOut, UsuarioCreate
from app.core.security import get_password_hash
from app.services.bitacora_service import registrar_bitacora

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])

@router.get(
    "/",
    response_model=List[UsuarioOut],
    dependencies=[Depends(require_roles(["administrador"]))]
)
def list_usuarios(
    rol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista usuarios registrados. Exclusivo para Administrador."""
    query = db.query(Usuario)
    if rol:
        query = query.filter(Usuario.rol.ilike(rol))
    return query.all()

@router.post(
    "/",
    response_model=UsuarioOut,
    dependencies=[Depends(require_roles(["administrador"]))]
)
def create_usuario(
    data: UsuarioCreate,
    current_admin: Usuario = Depends(require_roles(["administrador"])),
    db: Session = Depends(get_db)
):
    """Crea un nuevo usuario con rol específico (Administrador o Empleado)."""
    if db.query(Usuario).filter(Usuario.ci == data.ci).first():
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario con el CI {data.ci}")

    hashed_pw = get_password_hash(data.contrasena)
    nuevo_usuario = Usuario(
        ci=data.ci,
        nombre=data.nombre,
        contrasena=hashed_pw,
        rol=data.rol.lower().strip()
    )
    db.add(nuevo_usuario)
    db.flush()

    if nuevo_usuario.rol == "administrador":
        db.add(Administrador(ci=nuevo_usuario.ci))
    elif nuevo_usuario.rol in ["trabajador", "empleado"]:
        db.add(Empleado(ci=nuevo_usuario.ci))

    db.commit()

    registrar_bitacora(
        db=db,
        id_usuario=current_admin.ci,
        accion_realizada=f"CREACION_USUARIO: CI '{nuevo_usuario.ci}' con rol '{nuevo_usuario.rol}'",
        tabla_afectada="usuario"
    )

    return nuevo_usuario
