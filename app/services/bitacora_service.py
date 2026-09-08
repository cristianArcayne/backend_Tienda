from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import BitacoraUso, Usuario

def registrar_bitacora(
    db: Session, 
    id_usuario: Optional[str], 
    accion_realizada: str, 
    tabla_afectada: Optional[str] = "usuario"
) -> BitacoraUso:
    """Registra una acción en la tabla bitacora_uso de forma segura."""
    # Verificar si id_usuario existe como clave foránea válida
    usuario_valido = None
    if id_usuario:
        usuario_valido = db.query(Usuario.ci).filter(Usuario.ci == id_usuario).first()
        
    fk_usuario = id_usuario if usuario_valido else None
    detalle_accion = accion_realizada
    if id_usuario and not usuario_valido:
        detalle_accion = f"[{id_usuario}] - {accion_realizada}"

    registro = BitacoraUso(
        id_usuario=fk_usuario,
        accion_realizada=detalle_accion,
        tabla_afectada=tabla_afectada
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro
