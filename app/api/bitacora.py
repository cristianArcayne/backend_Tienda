from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.api.deps import get_db, require_roles
from app.models.models import BitacoraUso, Usuario
from app.schemas.schemas import BitacoraOut

router = APIRouter(prefix="/bitacora", tags=["Bitácora de Uso y Auditoría"])

@router.get(
    "/",
    response_model=List[BitacoraOut],
    dependencies=[Depends(require_roles(["administrador", "trabajador", "empleado"]))]
)
def get_bitacoras(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    id_usuario: Optional[str] = None,
    tabla: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna los registros de auditoría de bitacora_uso.
    ACCESO EXCLUSIVO: Administrador y Trabajador / Empleado.
    """
    query = db.query(BitacoraUso).outerjoin(Usuario, BitacoraUso.id_usuario == Usuario.ci)

    if id_usuario:
        query = query.filter(BitacoraUso.id_usuario == id_usuario)
    if tabla:
        query = query.filter(BitacoraUso.tabla_afectada.ilike(f"%{tabla}%"))
    if search:
        query = query.filter(BitacoraUso.accion_realizada.ilike(f"%{search}%"))

    registros = query.order_by(desc(BitacoraUso.fecha_hora), desc(BitacoraUso.id_bitacora)).offset(offset).limit(limit).all()

    # Formatear salida con datos del usuario relacionado
    resultado = []
    for reg in registros:
        nombre = reg.usuario.nombre if reg.usuario else None
        rol = reg.usuario.rol if reg.usuario else None
        
        resultado.append(BitacoraOut(
            id_bitacora=reg.id_bitacora,
            id_usuario=reg.id_usuario,
            fecha_hora=reg.fecha_hora,
            accion_realizada=reg.accion_realizada,
            tabla_afectada=reg.tabla_afectada,
            usuario_nombre=nombre,
            usuario_rol=rol
        ))

    return resultado
