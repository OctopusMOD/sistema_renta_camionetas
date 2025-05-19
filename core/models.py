from django.db import models

class Vehiculo(models.Model):
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField()
    placa = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=[
        ('disponible', 'Disponible'),
        ('alquilado', 'Alquilado'),
        ('mantenimiento', 'Mantenimiento')
    ])

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    licencia_conducir = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Alquiler(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    kilometraje_inicio = models.IntegerField()
    kilometraje_fin = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('completado', 'Completado')
    ])

    def __str__(self):
        return f"Alquiler {self.id} - {self.vehiculo} por {self.cliente}"
    
from django.db import models
from django.contrib.auth.models import User

class Taller(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    contacto = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Mantenimiento(models.Model):
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.CASCADE)
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    descripcion = models.TextField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('en progreso', 'En Progreso'),
            ('completado', 'Completado'),
            ('cancelado', 'Cancelado')
        ],
        default='en progreso'
    )
    encargado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Mantenimiento {self.id} - {self.vehiculo.placa}"

class LineaTrabajo(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='lineas_trabajo')
    descripcion = models.CharField(max_length=200)
    cantidad = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.valor_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} - ${self.total}"

class Repuesto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.IntegerField(default=0)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class RepuestoUsado(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE, related_name='repuestos_usados')
    repuesto = models.ForeignKey(Repuesto, on_delete=models.CASCADE)
    cantidad_usada = models.IntegerField()

    def __str__(self):
        return f"{self.repuesto.nombre} - {self.cantidad_usada}"