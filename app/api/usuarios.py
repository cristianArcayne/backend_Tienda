from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.models.models import Usuario, Administrador, Empleado, Cliente, Sucursal
from app.schemas.schemas import UsuarioDetailOut, UsuarioCreateFull, EmpresaConfig
from app.core.security import get_password_hash
from app.services.bitacora_service import registrar_bitacora

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios y Control de Roles"])

@router.get(
    "/",
    response_model=List[UsuarioDetailOut],
    dependencies=[Depends(require_roles(["administrador"]))]
)
def list_usuarios(
    rol: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los usuarios con sus detalles completos (Cliente, Empleado o Administrador).
    Exclusivo para el Administrador.
    """
    query = db.query(Usuario)
    if rol and rol.lower() != 'todos':
        # Permitir equivalencia entre trabajador y empleado
        if rol.lower() in ['trabajador', 'empleado']:
            query = query.filter(Usuario.rol.in_(['trabajador', 'empleado']))
        else:
            query = query.filter(Usuario.rol.ilike(rol.strip()))

    if search:
        query = query.filter(
            (Usuario.ci.ilike(f"%{search}%")) | (Usuario.nombre.ilike(f"%{search}%"))
        )

    usuarios = query.all()
    resultado = []

    for u in usuarios:
        item = UsuarioDetailOut(
            ci=u.ci,
            nombre=u.nombre,
            rol=u.rol
        )
        if u.cliente:
            item.apellido = u.cliente.apellido
            item.correo_electronico = u.cliente.correo_electronico
            item.telefono = u.cliente.telefono
            item.genero = u.cliente.genero
            item.edad = u.cliente.edad
        elif u.empleado:
            item.id_sucursal = u.empleado.id_sucursal
            if u.empleado.sucursal:
                item.sucursal_nombre = u.empleado.sucursal.nombre
        resultado.append(item)

    return resultado

@router.post(
    "/",
    response_model=UsuarioDetailOut,
    dependencies=[Depends(require_roles(["administrador"]))]
)
def create_usuario(
    data: UsuarioCreateFull,
    current_admin: Usuario = Depends(require_roles(["administrador"])),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario asignándole su rol correspondiente:
    - 'administrador' -> Se crea en 'usuario' y 'administrador'.
    - 'empleado' / 'trabajador' -> Se crea en 'usuario' y 'empleado'.
    - 'cliente' -> Se crea en 'usuario' y 'cliente'.
    """
    if db.query(Usuario).filter(Usuario.ci == data.ci).first():
        raise HTTPException(status_code=400, detail=f"Ya existe un usuario con el CI {data.ci}")

    clean_rol = data.rol.lower().strip()
    if clean_rol not in ['administrador', 'empleado', 'trabajador', 'cliente']:
        raise HTTPException(status_code=400, detail=f"Rol '{data.rol}' no válido. Use 'administrador', 'empleado' o 'cliente'.")

    # Si es cliente y puso correo, validar que no esté repetido
    if clean_rol == 'cliente' and data.correo_electronico:
        if db.query(Cliente).filter(Cliente.correo_electronico.ilike(data.correo_electronico)).first():
            raise HTTPException(status_code=400, detail=f"Ya existe un cliente con el correo {data.correo_electronico}")

    hashed_pw = get_password_hash(data.contrasena)
    nuevo_usuario = Usuario(
        ci=data.ci,
        nombre=data.nombre,
        contrasena=hashed_pw,
        rol=clean_rol
    )
    db.add(nuevo_usuario)
    db.flush()

    if clean_rol == "administrador":
        db.add(Administrador(ci=nuevo_usuario.ci))
    elif clean_rol in ["trabajador", "empleado"]:
        sucursal = db.query(Sucursal).first()
        id_suc = data.id_sucursal or (sucursal.id_sucursal if sucursal else None)
        db.add(Empleado(ci=nuevo_usuario.ci, id_sucursal=id_suc))
    elif clean_rol == "cliente":
        db.add(Cliente(
            ci=nuevo_usuario.ci,
            apellido=data.apellido or "",
            genero=data.genero or "No especificado",
            correo_electronico=data.correo_electronico or f"{data.ci}@cliente.com",
            telefono=data.telefono or "",
            edad=data.edad or 18
        ))

    db.commit()

    registrar_bitacora(
        db=db,
        id_usuario=current_admin.ci,
        accion_realizada=f"CONTROL_USUARIOS: Alta de usuario CI '{nuevo_usuario.ci}' con rol '{nuevo_usuario.rol}'",
        tabla_afectada="usuario"
    )

    # Construir respuesta detallada
    resp = UsuarioDetailOut(
        ci=nuevo_usuario.ci,
        nombre=nuevo_usuario.nombre,
        rol=nuevo_usuario.rol,
        apellido=data.apellido,
        correo_electronico=data.correo_electronico,
        telefono=data.telefono,
        genero=data.genero,
        edad=data.edad,
        id_sucursal=data.id_sucursal
    )
    return resp

@router.delete(
    "/{ci}",
    dependencies=[Depends(require_roles(["administrador"]))]
)
def delete_usuario(
    ci: str,
    current_admin: Usuario = Depends(require_roles(["administrador"])),
    db: Session = Depends(get_db)
):
    """Elimina un usuario del sistema (no permitido eliminarse a sí mismo)."""
    if ci == current_admin.ci:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta de administrador.")

    user = db.query(Usuario).filter(Usuario.ci == ci).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    rol = user.rol
    db.delete(user)
    db.commit()

    registrar_bitacora(
        db=db,
        id_usuario=current_admin.ci,
        accion_realizada=f"CONTROL_USUARIOS: Eliminación de usuario CI '{ci}' ({rol})",
        tabla_afectada="usuario"
    )

    return {"message": f"Usuario con CI {ci} eliminado correctamente."}

# CONFIGURACION DE EMPRESA (Para la pantalla mostrada a la derecha de la imagen)
_empresa_cache = EmpresaConfig()

@router.get("/empresa/config", response_model=EmpresaConfig)
def get_empresa_config():
    """Retorna los datos de configuración de la empresa."""
    return _empresa_cache

@router.post("/empresa/config", response_model=EmpresaConfig, dependencies=[Depends(require_roles(["administrador"]))])
def update_empresa_config(data: EmpresaConfig, current_admin: Usuario = Depends(require_roles(["administrador"])), db: Session = Depends(get_db)):
    """Actualiza la configuración de la empresa y audita el cambio."""
    global _empresa_cache
    _empresa_cache = data
    registrar_bitacora(
        db=db,
        id_usuario=current_admin.ci,
        accion_realizada="CONFIGURACION_SISTEMA: Actualización de datos de la empresa",
        tabla_afectada="sistema"
    )
    return _empresa_cache
