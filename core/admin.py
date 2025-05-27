# core/admin.py
from django.contrib import admin
from .models import Vehiculo, Cliente, Alquiler, Taller, Mantenimiento, Repuesto, TrabajoRealizado, Producto, Proveedor, MovimientoInventario, Marca, Modelo

# Admin para Marca
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']
    list_per_page = 25

# Admin para Modelo
@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca']
    search_fields = ['nombre', 'marca__nombre']
    list_filter = ['marca']
    list_per_page = 25

# Admin para Vehículo
@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'estado', 'anio')
    list_filter = ['estado', 'anio']
    search_fields = ['patente', 'marca__nombre', 'modelo__nombre']
    list_per_page = 25

# Admin para Cliente
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo', 'tipo_cliente')
    search_fields = ['nombre', 'correo', 'rut', 'razon_social']
    list_filter = ['tipo_cliente']
    list_per_page = 25

# Admin para Alquiler
@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ('numero_alquiler', 'vehiculo', 'cliente', 'fecha_inicio', 'fecha_termino', 'estado')
    list_filter = ['estado', 'fecha_inicio', 'fecha_termino']
    search_fields = ['numero_alquiler', 'vehiculo__patente', 'cliente__nombre', 'cliente__razon_social']
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vehiculo', 'cliente')

# Admin para Taller
@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercial', 'rut', 'telefono', 'ciudad')
    search_fields = ['nombre_comercial', 'rut', 'ciudad', 'contacto']
    list_filter = ['ciudad', 'region']
    ordering = ('nombre_comercial',)
    list_per_page = 25

# Admin para Repuesto
@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'unidades', 'valor_unidad', 'valor_total')  # Añadido valor_total como propiedad
    search_fields = ['producto__nombre', 'producto__codigo_referencia', 'codigo', 'nombre']
    list_filter = ['producto__categoria']
    list_per_page = 25

    def valor_total(self, obj):
        return obj.valor_total
    valor_total.short_description = 'Valor Total'

# Admin para TrabajoRealizado
@admin.register(TrabajoRealizado)
class TrabajoRealizadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'unidades', 'valor_unidad', 'valor_total')  # Añadido valor_total como propiedad
    search_fields = ['codigo', 'descripcion']
    list_filter = ['mantenimiento__tipo_mantenimiento']
    list_per_page = 25

    def valor_total(self, obj):
        return obj.valor_total
    valor_total.short_description = 'Valor Total'

# Inlines para el mantenimiento
class TrabajoRealizadoInline(admin.TabularInline):
    model = TrabajoRealizado
    extra = 1

class RepuestoInline(admin.TabularInline):
    model = Repuesto
    extra = 1

# Admin para Mantenimiento
@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehiculo', 'tipo_mantenimiento', 'fecha_ingreso', 'fecha_salida', 'confirmado']
    list_filter = ['tipo_mantenimiento', 'confirmado', 'fecha_ingreso']
    search_fields = ['vehiculo__patente', 'taller__nombre_comercial']
    inlines = [TrabajoRealizadoInline, RepuestoInline]
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vehiculo', 'taller')

# Admin para Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_referencia', 'unidades', 'valor_unitario', 'proveedor')
    search_fields = ['nombre', 'codigo_referencia']
    list_filter = ['categoria', 'proveedor']
    list_per_page = 25

# Admin para Proveedor
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo', 'contacto')  # Corregido a 'nombre' como campo principal
    search_fields = ['nombre', 'contacto', 'correo']
    list_per_page = 25

# Admin para MovimientoInventario
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'fecha', 'usuario')
    search_fields = ['producto__nombre', 'usuario__username']
    list_filter = ['tipo', 'fecha']
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producto', 'usuario')