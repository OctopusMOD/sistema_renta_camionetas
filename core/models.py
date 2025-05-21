from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Constantes para elecciones
TIPO_MANTENIMIENTO = [
    ('preventivo', 'Preventivo'),
    ('correctivo', 'Correctivo'),
]

ESTADO_ORDEN = [
    ('en_proceso',    'En Proceso'),
    ('completado',    'Completado'),
    ('cancelado',     'Cancelado'),
]

NIVEL_COMBUSTIBLE = [
    ('lleno',         'Lleno'),
    ('3/4',           '3/4'),
    ('1/2',           '1/2'),
    ('1/4',           '1/4'),
    ('vacío',         'Vacío'),
    ('no_especifica', 'No especifica'),
]

CATEGORIAS_TRABAJO = [
    ('mecanica',      'Mecánica'),
    ('electricidad',  'Electricidad'),
    ('chapa',         'Chapa y Pintura'),
]

# Modelos principales
class Vehiculo(models.Model):
    marca   = models.CharField(max_length=50)
    modelo  = models.CharField(max_length=50)
    anio    = models.IntegerField()
    patente = models.CharField(max_length=20, unique=True)
    estado  = models.CharField(
        max_length=20,
        choices=[
            ('disponible',    'Disponible'),
            ('alquilado',     'Alquilado'),
            ('mantenimiento', 'Mantenimiento'),
        ]
    )

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"


class Cliente(models.Model):
    nombre             = models.CharField(max_length=100)
    telefono           = models.CharField(max_length=20)
    correo             = models.EmailField()
    licencia_conducir  = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Alquiler(models.Model):
    vehiculo           = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    cliente            = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_inicio       = models.DateField()
    fecha_fin          = models.DateField()
    kilometraje_inicio = models.IntegerField()
    kilometraje_fin    = models.IntegerField(null=True, blank=True)
    estado             = models.CharField(
        max_length=20,
        choices=[('activo', 'Activo'), ('completado', 'Completado')]
    )

    def __str__(self):
        return f"Alquiler {self.id} - {self.vehiculo} por {self.cliente}"


class Taller(models.Model):
    nombre    = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono  = models.CharField(max_length=20)
    contacto  = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Mantenimiento(models.Model):
    orden_trabajo       = models.AutoField(primary_key=True)
    vehiculo            = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True)
    tipo                = models.CharField(max_length=20, choices=TIPO_MANTENIMIENTO)
    kilometraje_ingreso = models.PositiveIntegerField()
    nivel_combustible   = models.CharField(max_length=20, choices=NIVEL_COMBUSTIBLE)
    taller              = models.ForeignKey(Taller, on_delete=models.SET_NULL, null=True)
    fecha_ingreso       = models.DateField(default=timezone.now)
    fecha_fin           = models.DateField(null=True, blank=True)
    estado              = models.CharField(max_length=20, choices=ESTADO_ORDEN, default='en_proceso')
    observaciones       = models.TextField(blank=True, null=True)
    encargado           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        veh = self.vehiculo.patente if self.vehiculo else 'Sin vehículo'
        return f"OT {self.orden_trabajo} - {veh}"


class TrabajoRealizado(models.Model):
    mantenimiento     = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='trabajos')
    categoria         = models.CharField(max_length=50, choices=CATEGORIAS_TRABAJO)
    descripcion       = models.CharField(max_length=255)
    unidades          = models.PositiveIntegerField()
    precio_unitario   = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total      = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.precio_total = self.unidades * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categoria}: {self.descripcion} - ${self.precio_total}"


class Repuesto(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad    = models.IntegerField(default=0)
    costo       = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


class RepuestoUtilizado(models.Model):
    mantenimiento    = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='repuestos_libres')
    nombre           = models.CharField(max_length=100)
    costo            = models.DecimalField(max_digits=10, decimal_places=2)
    desde_inventario = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - ${self.costo}"


class RepuestoUsado(models.Model):
    mantenimiento   = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='repuestos_inventario')
    repuesto        = models.ForeignKey(Repuesto, on_delete=models.CASCADE)
    cantidad_usada  = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.repuesto.nombre} x{self.cantidad_usada}"


class DocumentoAdjunto(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='documentos')
    archivo       = models.FileField(upload_to='documentos_mantenimiento/')

    def __str__(self):
        return f"Doc OT {self.mantenimiento.orden_trabajo}"


class LineaTrabajo(models.Model):
    mantenimiento = models.ForeignKey('Mantenimiento', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} (x{self.cantidad})"
