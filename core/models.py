from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

# Helper function for default date
def get_default_date():
    return timezone.now().date()

# Constantes para elecciones
TIPO_MANTENIMIENTO = [
    ('preventivo', 'Preventivo'),
    ('correctivo', 'Correctivo'),
]

NIVEL_COMBUSTIBLE = [
    ('1/8', '1/8'),
    ('2/8', '2/8'),
    ('3/8', '3/8'),
    ('4/8', '4/8'),
    ('5/8', '5/8'),
    ('6/8', '6/8'),
    ('7/8', '7/8'),
    ('8/8', '8/8'),
    ('N/A', 'N/A'),
]

class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Modelo(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    nombre = models.CharField(max_length=50)

    class Meta:
        unique_together = ('marca', 'nombre')

    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"

class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, unique=True, verbose_name="Patente")
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Marca")
    modelo = models.ForeignKey(Modelo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Modelo")
    anio = models.IntegerField(verbose_name="Año")
    kilometraje = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Kilometraje")
    color = models.CharField(max_length=20, blank=True, verbose_name="Color")
    vin = models.CharField(max_length=70, unique=True, blank=True, verbose_name="VIN")
    combustible = models.CharField(max_length=20, choices=[
        ('Gasolina', 'Gasolina'),
        ('Diésel', 'Diésel'),
        ('Eléctrico', 'Eléctrico')
    ], default='Gasolina', verbose_name="Combustible")
    transmision = models.CharField(max_length=20, choices=[
        ('Manual', 'Manual'),
        ('Automática', 'Automática')
    ], default='Manual', verbose_name="Transmisión")
    traccion = models.CharField(max_length=10, choices=[
        ('4x4', '4x4'),
        ('4x2', '4x2')
    ], default='4x2', verbose_name="Tracción")
    capacidad_estanque = models.FloatField(validators=[MinValueValidator(0)], verbose_name="Capacidad del Estanque (litros)")
    cilindrada = models.FloatField(validators=[MinValueValidator(0)], verbose_name="Cilindrada del Motor (cc)")
    capacidad_carga = models.FloatField(validators=[MinValueValidator(0)], verbose_name="Capacidad de Carga (kg)")
    estado = models.CharField(max_length=20, choices=[
        ('disponible', 'Disponible'),
        ('alquilado', 'Alquilado'),
        ('mantenimiento', 'Mantenimiento')
    ], default='disponible', verbose_name="Estado")
    fecha_registro = models.DateField(default=get_default_date, verbose_name="Fecha de Registro")
    permiso_circulacion = models.DateField(default=get_default_date, verbose_name="Permiso de Circulación (Fecha de Vencimiento)")
    soap = models.DateField(default=get_default_date, verbose_name="SOAP (Fecha de Vencimiento)")
    revision_tecnica = models.DateField(default=get_default_date, verbose_name="Revisión Técnica (Fecha de Vencimiento)")

    def __str__(self):
        return f"{self.marca.nombre if self.marca else 'Sin marca'} {self.modelo.nombre if self.modelo else 'Sin modelo'} ({self.patente})"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('natural', 'Persona Natural'),
        ('empresa', 'Empresa'),
    ]

    tipo_cliente = models.CharField(
        max_length=10,
        choices=TIPO_CLIENTE_CHOICES,
        default='natural',
        help_text='Tipo de cliente'
    )

    # Campos para Persona Natural
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True, help_text='Ej: 12.345.678-9')
    nombre = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(max_length=255, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True, help_text='Ej: Av. Siempre Viva 123, Santiago')
    licencia_conducir = models.CharField(max_length=50, unique=True, blank=True, null=True)

    # Campos para Empresa
    razon_social = models.CharField(max_length=100, blank=True, null=True)
    rut_empresa = models.CharField(max_length=12, unique=True, blank=True, null=True, help_text='Ej: 76.543.210-5')
    contacto_principal = models.CharField(max_length=100, blank=True, null=True)
    telefono_empresa = models.CharField(max_length=20, blank=True, null=True)
    correo_empresa = models.EmailField(max_length=255, blank=True, null=True)
    giro = models.CharField(max_length=100, blank=True, null=True)
    direccion_fiscal = models.TextField(blank=True, null=True, help_text='Ej: Av. Principal 456, Santiago')

    def __str__(self):
        if self.tipo_cliente == 'natural':
            return self.nombre or 'Sin nombre'
        return self.razon_social or 'Sin razón social'

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.tipo_cliente == 'natural':
            if not self.rut or not self.nombre or not self.telefono or not self.correo or not self.licencia_conducir:
                raise ValidationError("Todos los campos de Persona Natural son obligatorios.")
            if Cliente.objects.exclude(id=self.id).filter(rut=self.rut).exists():
                raise ValidationError("El RUT ya está registrado.")
            if Cliente.objects.exclude(id=self.id).filter(licencia_conducir=self.licencia_conducir).exists():
                raise ValidationError("La licencia de conducir ya está registrada.")
        elif self.tipo_cliente == 'empresa':
            if not self.razon_social or not self.rut_empresa or not self.contacto_principal or not self.telefono_empresa or not self.correo_empresa or not self.giro or not self.direccion_fiscal:
                raise ValidationError("Todos los campos de Empresa son obligatorios.")
            if Cliente.objects.exclude(id=self.id).filter(rut_empresa=self.rut_empresa).exists():
                raise ValidationError("El RUT de la empresa ya está registrado.")

class Alquiler(models.Model):
    TIPO_ALQUILER_CHOICES = [
        ('contrato', 'Contrato'),
        ('reserva', 'Reserva'),
    ]

    tipo_alquiler = models.CharField(max_length=10, choices=TIPO_ALQUILER_CHOICES, default='contrato')
    numero_alquiler = models.CharField(max_length=10, unique=True)
    tipo_cliente = models.CharField(max_length=10, choices=Cliente.TIPO_CLIENTE_CHOICES, default='natural')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='alquileres', verbose_name="Vehículo")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='alquileres', verbose_name="Cliente")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_termino = models.DateField(verbose_name="Fecha de Término")
    valor_diario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valor Diario")
    garantia = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Garantía")
    anotaciones_internas = models.TextField(blank=True, verbose_name="Anotaciones Internas")
    anotaciones_publicas = models.TextField(blank=True, verbose_name="Anotaciones Públicas")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Creado Por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    estado = models.CharField(
        max_length=20,
        choices=[('activo', 'Activo'), ('completado', 'Completado')],
        default='activo',
        verbose_name="Estado"
    )
    nivel_combustible_entrega = models.CharField(max_length=20, choices=NIVEL_COMBUSTIBLE, verbose_name="Nivel de Combustible al Entregar")

    def __str__(self):
        return f"{self.tipo_alquiler.capitalize()} {self.numero_alquiler} - {self.vehiculo.patente}"

    class Meta:
        verbose_name = "Alquiler"
        verbose_name_plural = "Alquileres"

class Extra(models.Model):
    alquiler = models.ForeignKey(Alquiler, related_name='extras', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.PositiveIntegerField(default=1)

    def total(self):
        return self.valor * self.unidades

    def __str__(self):
        return f"{self.descripcion} - {self.total()}"

class Factura(models.Model):
    alquiler = models.ForeignKey(Alquiler, related_name='facturas', on_delete=models.CASCADE)
    numero_factura = models.CharField(max_length=20)
    fecha_emision = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.monto}"

class Taller(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre_legal = models.CharField(max_length=100)
    nombre_comercial = models.CharField(max_length=100)
    giro = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo_electronico = models.EmailField(blank=True)
    numero_interno = models.CharField(max_length=20, blank=True)
    servicios = models.TextField(blank=True)
    horario_atencion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_comercial

    class Meta:
        verbose_name = "Taller"
        verbose_name_plural = "Talleres"

class Mantenimiento(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='mantenimientos', verbose_name="Vehículo")
    marca_modelo = models.CharField(max_length=100, verbose_name="Marca / Modelo")
    kilometraje = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Kilometraje")
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPO_MANTENIMIENTO, verbose_name="Tipo de Mantenimiento")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso", null=False, blank=False)
    fecha_salida = models.DateField(verbose_name="Fecha de Salida", null=True, blank=True)
    nivel_combustible = models.CharField(max_length=20, choices=NIVEL_COMBUSTIBLE, verbose_name="Nivel de Combustible")
    encargado = models.CharField(max_length=100, blank=True, verbose_name="Encargado")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    taller = models.ForeignKey(Taller, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Taller")
    confirmado = models.BooleanField(default=False, verbose_name="Confirmado")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mantenimientos_creados', verbose_name="Creado Por")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado En")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado En")

    def __str__(self):
        return f"Mantenimiento {self.id} - {self.vehiculo.patente} ({'Confirmado' if self.confirmado else 'Pendiente'})"

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"

class TrabajoRealizado(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='trabajos', verbose_name="Mantenimiento")
    codigo = models.CharField(max_length=50, verbose_name="Código")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    unidades = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Unidades")
    valor_unidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valor Unitario")

    @property
    def valor_total(self):
        return self.unidades * self.valor_unidad

    def __str__(self):
        return f"Trabajo {self.codigo} - {self.descripción} (Mantenimiento {self.mantenimiento.id})"

    class Meta:
        verbose_name = "Trabajo Realizado"
        verbose_name_plural = "Trabajos Realizados"

class Repuesto(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='repuestos', verbose_name="Mantenimiento")
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, verbose_name="Producto", null=True, blank=True)
    codigo = models.CharField(max_length=50, blank=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, blank=True, verbose_name="Nombre")
    unidades = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Unidades")
    valor_unidad = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)], verbose_name="Valor Unitario")

    @property
    def valor_total(self):
        return self.unidades * self.valor_unidad

    def __str__(self):
        return f"Repuesto {self.codigo or self.producto.codigo_referencia if self.producto else 'Sin código'} - {self.nombre or self.producto.nombre if self.producto else 'Sin nombre'} (Mantenimiento {self.mantenimiento.id})"

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    correo = models.EmailField(verbose_name="Correo Electrónico")
    direccion = models.TextField(verbose_name="Dirección")
    contacto = models.CharField(max_length=100, verbose_name="Persona de Contacto")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

class Producto(models.Model):
    CATEGORIAS = [
        ('Filtros', 'Filtros'),
        ('Aceites', 'Aceites'),
        ('Neumáticos', 'Neumáticos'),
        ('Otros', 'Otros'),
    ]
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='Otros', verbose_name="Categoría")
    codigo_referencia = models.CharField(max_length=20, unique=True, verbose_name="Código de Referencia")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Valor Unitario")
    unidades = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Unidades en Stock")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    fecha_ultima_actualizacion = models.DateField(auto_now=True, verbose_name="Fecha de Última Actualización")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return f"{self.nombre} ({self.codigo_referencia})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('Ingreso', 'Ingreso'),
        ('Salida', 'Salida'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO, verbose_name="Tipo de Movimiento")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mantenimiento")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    notas = models.TextField(blank=True, verbose_name="Notas")

    def __str__(self):
        return f"{self.tipo} - {self.cantidad} de {self.producto.nombre} ({self.fecha})"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"