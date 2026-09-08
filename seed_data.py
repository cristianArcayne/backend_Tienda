"""
Script para inicializar datos semilla de prueba en bd_tienda_virtual
"""
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.models import (
    Usuario, Administrador, Empleado, Cliente, Sucursal, 
    Categoria, Temporada, Color, Talla, Ropa, BitacoraUso
)

def seed():
    db = SessionLocal()
    try:
        print("Iniciando carga de datos semilla en bd_tienda_virtual...")

        # 1. Sucursal principal
        sucursal = db.query(Sucursal).first()
        if not sucursal:
            sucursal = Sucursal(
                nombre="Atelier Central - París",
                direccion="Rue Saint-Honoré 245",
                telefono="+33 1 42 68 55 00"
            )
            db.add(sucursal)
            db.flush()
            print("[OK] Sucursal creada")
        else:
            print("[OK] Sucursal existente encontrada")

        # 2. Administrador
        admin_ci = "1001"
        admin = db.query(Usuario).filter(Usuario.ci == admin_ci).first()
        if not admin:
            admin = Usuario(
                ci=admin_ci,
                nombre="Gabriel Laurent",
                contrasena=get_password_hash("admin123"),
                rol="administrador"
            )
            db.add(admin)
            db.flush()
            db.add(Administrador(ci=admin_ci))
            print(f"[OK] Administrador creado: CI {admin_ci} / admin123")
        else:
            print("[OK] Administrador ya existe")

        # 3. Trabajador / Empleado
        empleado_ci = "2001"
        empleado = db.query(Usuario).filter(Usuario.ci == empleado_ci).first()
        if not empleado:
            empleado = Usuario(
                ci=empleado_ci,
                nombre="Marc Dupont",
                contrasena=get_password_hash("trabajador123"),
                rol="trabajador"
            )
            db.add(empleado)
            db.flush()
            db.add(Empleado(ci=empleado_ci, id_sucursal=sucursal.id_sucursal))
            print(f"[OK] Trabajador creado: CI {empleado_ci} / trabajador123")
        else:
            print("[OK] Trabajador ya existe")

        # 4. Cliente
        cliente_ci = "3001"
        cliente_user = db.query(Usuario).filter(Usuario.ci == cliente_ci).first()
        if not cliente_user:
            cliente_user = Usuario(
                ci=cliente_ci,
                nombre="Éléonore Moreau",
                contrasena=get_password_hash("cliente123"),
                rol="cliente"
            )
            db.add(cliente_user)
            db.flush()
            cliente_detalles = Cliente(
                ci=cliente_ci,
                apellido="Moreau",
                genero="Femenino",
                correo_electronico="atelier@maison.com",
                telefono="+33 6 12 34 56 78",
                edad=28
            )
            db.add(cliente_detalles)
            print(f"[OK] Cliente creado: CI {cliente_ci} (atelier@maison.com) / cliente123")
        else:
            print("[OK] Cliente ya existe")

        # 5. Categoría y Temporada
        cat = db.query(Categoria).first()
        if not cat:
            cat = Categoria(nombre="Haute Couture", descripcion="Prendas exclusivas a medida")
            db.add(cat)
            db.flush()

        temp = db.query(Temporada).first()
        if not temp:
            temp = Temporada(nombre="Otoño / Invierno 2026")
            db.add(temp)
            db.flush()

        # 6. Prendas de demostración para el Atelier
        if db.query(Ropa).count() == 0:
            ropa1 = Ropa(
                id_categoria=cat.id_categoria,
                id_temporada=temp.id_temporada,
                nombre="Saco Estructural Asimétrico",
                descripcion="Confección en lana virgen y caída contemporánea.",
                precio=850.00,
                estado="Disponible",
                edad_estimada="Adulto"
            )
            ropa2 = Ropa(
                id_categoria=cat.id_categoria,
                id_temporada=temp.id_temporada,
                nombre="Pantalón Plisado Silueta Amplia",
                descripcion="Corte fluido con pinzas invertidas en tono antracita.",
                precio=420.00,
                estado="Disponible",
                edad_estimada="Adulto"
            )
            db.add_all([ropa1, ropa2])
            print("[OK] Prendas de catálogo creadas")

        # 7. Registros de prueba en Bitácora
        if db.query(BitacoraUso).count() == 0:
            db.add_all([
                BitacoraUso(
                    id_usuario=admin_ci,
                    accion_realizada="INICIALIZACION_SISTEMA: Carga de configuración inicial",
                    tabla_afectada="sistema"
                ),
                BitacoraUso(
                    id_usuario=empleado_ci,
                    accion_realizada="INICIO_SESION_EXITOSO: Apertura de turno",
                    tabla_afectada="usuario"
                ),
                BitacoraUso(
                    id_usuario=cliente_ci,
                    accion_realizada="REGISTRO_CLIENTE_EXITOSO: atelier@maison.com",
                    tabla_afectada="cliente"
                )
            ])
            print("[OK] Registros iniciales de bitácora creados")

        db.commit()
        print("\n¡Semillado completado con éxito!")
        print("-" * 50)
        print("USUARIOS LISTOS PARA INICIAR SESIÓN:")
        print("1. Administrador:")
        print("   - Login: 1001 (o admin@atelier.com)")
        print("   - Contraseña: admin123")
        print("2. Trabajador:")
        print("   - Login: 2001")
        print("   - Contraseña: trabajador123")
        print("3. Cliente (el del mockup):")
        print("   - Login: atelier@maison.com (o 3001)")
        print("   - Contraseña: cliente123")
        print("-" * 50)

    except Exception as e:
        db.rollback()
        print("Error durante el semillado:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
