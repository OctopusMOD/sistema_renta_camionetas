from django.contrib import admin
from .models import (
    Vehiculo, Cliente, Alquiler, Taller,
    Mantenimiento, TrabajoRealizado,
    Repuesto, RepuestoUtilizado,
    RepuestoUsado, DocumentoAdjunto
)

# Admin básico
@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'patente', 'estado')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo')

@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'cliente', 'fecha_inicio', 'fecha_fin', 'estado')

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'contacto')

@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'costo')

# Inlines para el mantenimiento
class TrabajoInline(admin.TabularInline):
    model = TrabajoRealizado
    extra = 1

class RepuestoLibreInline(admin.TabularInline):
    model = RepuestoUtilizado
    extra = 1

class RepuestoInventarioInline(admin.TabularInline):
    model = RepuestoUsado
    extra = 1

class DocumentoInline(admin.TabularInline):
    model = DocumentoAdjunto
    extra = 1

# Admin de Mantenimiento
@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ['orden_trabajo', 'vehiculo', 'tipo', 'fecha_ingreso', 'estado']
    inlines = [TrabajoInline, RepuestoLibreInline, RepuestoInventarioInline, DocumentoInline]
