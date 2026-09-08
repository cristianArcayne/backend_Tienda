from sqlalchemy import Column, Integer, String, Numeric, Text, Date, Time, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    ci = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    # En PostgreSQL la columna tiene el caracter con tilde/eñe
    contrasena = Column("contraseña", String, nullable=False)
    rol = Column(String, nullable=False)  # 'administrador', 'empleado' (o 'trabajador'), 'cliente'

    # Relaciones
    administrador = relationship("Administrador", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    empleado = relationship("Empleado", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    cliente = relationship("Cliente", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    bitacoras = relationship("BitacoraUso", back_populates="usuario", cascade="all, delete-orphan")

class Administrador(Base):
    __tablename__ = "administrador"

    ci = Column(String, ForeignKey("usuario.ci"), primary_key=True)
    usuario = relationship("Usuario", back_populates="administrador")

class Sucursal(Base):
    __tablename__ = "sucursal"

    id_sucursal = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String)
    telefono = Column(String)

    empleados = relationship("Empleado", back_populates="sucursal")
    almacenes = relationship("Almacen", back_populates="sucursal")
    pedidos = relationship("Pedido", back_populates="sucursal")
    reservas = relationship("ReservaCita", back_populates="sucursal")

class Empleado(Base):
    __tablename__ = "empleado"

    ci = Column(String, ForeignKey("usuario.ci"), primary_key=True)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"), nullable=True)

    usuario = relationship("Usuario", back_populates="empleado")
    sucursal = relationship("Sucursal", back_populates="empleados")

class Cliente(Base):
    __tablename__ = "cliente"

    ci = Column(String, ForeignKey("usuario.ci"), primary_key=True)
    apellido = Column(String)
    genero = Column(String)
    correo_electronico = Column(String, index=True)
    telefono = Column(String)
    edad = Column(Integer)

    usuario = relationship("Usuario", back_populates="cliente")
    pedidos = relationship("Pedido", back_populates="cliente")
    reservas = relationship("ReservaCita", back_populates="cliente")

class BitacoraUso(Base):
    __tablename__ = "bitacora_uso"

    id_bitacora = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(String, ForeignKey("usuario.ci"), nullable=True)
    fecha_hora = Column(DateTime, server_default=func.now(), default=func.now())
    accion_realizada = Column(String, nullable=False)
    tabla_afectada = Column(String, nullable=True)

    usuario = relationship("Usuario", back_populates="bitacoras")

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)

    ropas = relationship("Ropa", back_populates="categoria")

class Temporada(Base):
    __tablename__ = "temporada"

    id_temporada = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    ropas = relationship("Ropa", back_populates="temporada")

class Color(Base):
    __tablename__ = "color"

    id_color = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    hex = Column(String)

    ropa_variantes = relationship("RopaTallaColor", back_populates="color")

class Talla(Base):
    __tablename__ = "talla"

    id_talla = Column(Integer, primary_key=True, index=True)
    pais = Column(String)
    talla = Column(String, nullable=False)
    medida_cm = Column(String)

    ropa_variantes = relationship("RopaTallaColor", back_populates="talla")

class Proveedor(Base):
    __tablename__ = "proveedor"

    id_proveedor = Column(Integer, primary_key=True, index=True)
    telefono = Column(String)
    detalle = Column(Text)

    almacenes = relationship("Almacen", back_populates="proveedor")

class Almacen(Base):
    __tablename__ = "almacen"

    id_almacen = Column(Integer, primary_key=True, index=True)
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"))
    id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor"))
    nombre = Column(String, nullable=False)

    sucursal = relationship("Sucursal", back_populates="almacenes")
    proveedor = relationship("Proveedor", back_populates="almacenes")
    ropa_variantes = relationship("RopaTallaColor", back_populates="almacen")

class Ropa(Base):
    __tablename__ = "ropa"

    id_ropa = Column(Integer, primary_key=True, index=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))
    id_temporada = Column(Integer, ForeignKey("temporada.id_temporada"))
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    estado = Column(String)
    edad_estimada = Column(String)

    categoria = relationship("Categoria", back_populates="ropas")
    temporada = relationship("Temporada", back_populates="ropas")
    variantes = relationship("RopaTallaColor", back_populates="ropa")

class RopaTallaColor(Base):
    __tablename__ = "ropa_talla_color"

    id_talla_color = Column(Integer, primary_key=True, index=True)
    id_ropa = Column(Integer, ForeignKey("ropa.id_ropa"))
    id_talla = Column(Integer, ForeignKey("talla.id_talla"))
    id_color = Column(Integer, ForeignKey("color.id_color"))
    id_almacen = Column(Integer, ForeignKey("almacen.id_almacen"))
    stock = Column(Integer, default=0)

    ropa = relationship("Ropa", back_populates="variantes")
    talla = relationship("Talla", back_populates="ropa_variantes")
    color = relationship("Color", back_populates="ropa_variantes")
    almacen = relationship("Almacen", back_populates="ropa_variantes")

class ReservaCita(Base):
    __tablename__ = "reserva_cita"

    id_reserva = Column(Integer, primary_key=True, index=True)
    ci = Column(String, ForeignKey("cliente.ci"))
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"))
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String, default="Pendiente")

    cliente = relationship("Cliente", back_populates="reservas")
    sucursal = relationship("Sucursal", back_populates="reservas")
    detalles = relationship("DetalleReserva", back_populates="reserva")

class DetalleReserva(Base):
    __tablename__ = "detalle_reserva"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_reserva = Column(Integer, ForeignKey("reserva_cita.id_reserva"))
    id_talla_color = Column(Integer, ForeignKey("ropa_talla_color.id_talla_color"))
    cantidad = Column(Integer, default=1)

    reserva = relationship("ReservaCita", back_populates="detalles")

class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido = Column(Integer, primary_key=True, index=True)
    ci = Column(String, ForeignKey("cliente.ci"))
    id_sucursal = Column(Integer, ForeignKey("sucursal.id_sucursal"))
    total = Column(Numeric(10, 2), default=0.0)
    estado = Column(String, default="Pendiente")
    fecha = Column(DateTime, server_default=func.now())

    cliente = relationship("Cliente", back_populates="pedidos")
    sucursal = relationship("Sucursal", back_populates="pedidos")
    detalles = relationship("DetalleVenta", back_populates="pedido")
    pagos = relationship("Pago", back_populates="pedido")
    envios = relationship("Envios", back_populates="pedido")
    facturas = relationship("Factura", back_populates="pedido")

class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"))
    id_talla_color = Column(Integer, ForeignKey("ropa_talla_color.id_talla_color"))
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")

class Pago(Base):
    __tablename__ = "pago"

    id_pago = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"))
    metodo_pago = Column(String, nullable=False)
    fecha_pago = Column(DateTime, server_default=func.now())
    monto = Column(Numeric(10, 2), nullable=False)
    estado = Column(String, default="Completado")

    pedido = relationship("Pedido", back_populates="pagos")

class Envios(Base):
    __tablename__ = "envios"

    id_envio = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"))
    direccion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    fecha_envio = Column(Date)
    fecha_entrega = Column(Date)
    estado = Column(String, default="En camino")

    pedido = relationship("Pedido", back_populates="envios")

class Factura(Base):
    __tablename__ = "factura"

    nro_factura = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"))
    nombre = Column(String, nullable=False)
    nit = Column(String, nullable=False)
    fecha = Column(Date, server_default=func.current_date())
    total = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="facturas")
