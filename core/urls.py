from django.urls import path
from . import views

urlpatterns = [
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('agregar_vehiculo/', views.agregar_vehiculo, name='agregar_vehiculo'),
    path('vehiculo/<int:pk>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('vehiculo/<int:pk>/editar/', views.editar_vehiculo, name='editar_vehiculo'),
    path('vehiculo/<int:pk>/eliminar/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('alquileres/', views.lista_alquileres, name='lista_alquileres'),
    path('agregar_alquiler/', views.agregar_alquiler, name='agregar_alquiler'),
    path('alquiler/<int:pk>/devolver/', views.devolver_alquiler, name='devolver_alquiler'),
    path('mantenimientos/', views.lista_mantenimientos, name='lista_mantenimientos'),
    path('agregar_mantenimiento/', views.agregar_mantenimiento, name='agregar_mantenimiento'),
    path('mantenimiento/<int:pk>/editar/', views.editar_mantenimiento, name='editar_mantenimiento'),
    path('mantenimiento/<int:pk>/eliminar/', views.eliminar_mantenimiento, name='eliminar_mantenimiento'),
]