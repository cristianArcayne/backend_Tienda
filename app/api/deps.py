from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    ci: str = payload.get("sub")
    if ci is None:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.ci == ci).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en el sistema"
        )
    return user

def require_roles(allowed_roles: List[str]):
    """Validador de roles permitidos para un endpoint."""
    def role_checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        # Normalizar para admitir variaciones como 'trabajador' y 'empleado'
        normalized_user_role = current_user.rol.lower().strip()
        normalized_allowed = [r.lower().strip() for r in allowed_roles]
        
        # Permitir equivalencia entre 'trabajador' y 'empleado'
        has_role = (
            normalized_user_role in normalized_allowed or
            (normalized_user_role in ["trabajador", "empleado"] and any(r in ["trabajador", "empleado"] for r in normalized_allowed))
        )
        
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
