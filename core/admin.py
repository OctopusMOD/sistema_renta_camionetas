from django.contrib import admin
from .models import Vehiculo, Cliente, Alquiler

admin.site.register(Vehiculo)
admin.site.register(Cliente)
admin.site.register(Alquiler)

from django.contrib import admin
from .models import Vehiculo, Cliente, Alquiler, Taller, Mantenimiento, LineaTrabajo, Repuesto, RepuestoUsado

admin.site.register(Taller)
admin.site.register(Mantenimiento)
admin.site.register(LineaTrabajo)
admin.site.register(Repuesto)
admin.site.register(RepuestoUsado)