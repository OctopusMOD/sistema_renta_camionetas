from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Página Principal
    path('', views.index, name='index'),
    
    # Vehículos
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/agregar/', views.agregar_vehiculo, name='agregar_vehiculo'),
    path('vehiculos/<int:pk>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('vehiculos/<int:pk>/editar/', views.editar_vehiculo, name='editar_vehiculo'),
    path('vehiculos/<int:pk>/eliminar/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    path('vehiculos/flota-activa/', views.lista_flota_activa, name='lista_flota_activa'),
    path('gestion-categorias/', views.gestion_categorias, name='gestion_categorias'),

    # Clientes
    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),

    # Alquileres
    path('alquileres/', views.lista_alquileres, name='lista_alquileres'),
    path('alquileres/agregar/', views.agregar_alquiler, name='agregar_alquiler'),
    path('alquileres/<int:pk>/editar/', views.editar_alquiler, name='editar_alquiler'),
    path('alquileres/<int:pk>/devolver/', views.devolver_alquiler, name='devolver_alquiler'),
    path('alquileres/<int:pk>/eliminar/', views.eliminar_alquiler, name='eliminar_alquiler'),

    # Mantenimientos
    path('mantenimientos/', views.lista_mantenimientos, name='lista_mantenimientos'),
    path('mantenimientos/agregar/', views.agregar_mantenimiento, name='agregar_mantenimiento'),
    path('mantenimientos/<int:pk>/editar/', views.editar_mantenimiento, name='editar_mantenimiento'),
    path('mantenimientos/<int:pk>/eliminar/', views.eliminar_mantenimiento, name='eliminar_mantenimiento'),

    # Talleres
    path('talleres/', views.lista_talleres, name='lista_talleres'),
    path('talleres/gestionar/', views.gestionar_talleres, name='gestionar_talleres'),
    path('talleres/<int:pk>/editar/', views.editar_taller, name='editar_taller'),
    path('talleres/<int:pk>/eliminar/', views.eliminar_taller, name='eliminar_taller'),

    # Bodega
    path('bodega/', views.bodega, name='bodega'),
    path('bodega/ingreso/', views.ingreso_articulos, name='ingreso_articulos'),
    path('bodega/proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('bodega/proveedores/agregar/', views.agregar_proveedor, name='agregar_proveedor'),
    path('bodega/producto/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('bodega/producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('bodega/buscar-producto/', views.buscar_producto, name='buscar_producto'),

    # Alertas
    path('alertas/', views.alertas, name='alertas'),

    # Utilidades
    path('test-form/', views.test_form, name='test_form'),
    path('check-patente/', views.check_patente, name='check_patente'),
    path('check-codigo-trabajo/', views.check_codigo_trabajo, name='check_codigo_trabajo'),
    path('check-codigo-repuesto/', views.check_codigo_repuesto, name='check_codigo_repuesto'),
    path('check-stock/', views.check_stock, name='check_stock'),
]