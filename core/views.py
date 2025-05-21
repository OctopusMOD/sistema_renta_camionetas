from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Vehiculo, Alquiler, Mantenimiento
from .forms import (
    VehiculoForm, AlquilerForm, MantenimientoForm,
    LineaTrabajoFormSet, RepuestoUsadoFormSet,
    RepuestoUtilizadoFormSet, DocumentoFormSet
)
from django.db.models import Q

# ---------- Vehículos ----------
@login_required
def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'core/lista_vehiculos.html', {'vehiculos': vehiculos})

@login_required
def agregar_vehiculo(request):
    form = VehiculoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_vehiculos')
    return render(request, 'core/agregar_vehiculo.html', {'form': form})

@login_required
def detalle_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    return render(request, 'core/detalle_vehiculo.html', {'vehiculo': vehiculo})

@login_required
def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, instance=vehiculo)
    if form.is_valid():
        form.save()
        return redirect('lista_vehiculos')
    return render(request, 'core/editar_vehiculo.html', {'form': form, 'vehiculo': vehiculo})

@login_required
def eliminar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == 'POST':
        vehiculo.delete()
        return redirect('lista_vehiculos')
    return render(request, 'core/eliminar_vehiculo.html', {'vehiculo': vehiculo})

# ---------- Autenticación ----------
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('lista_vehiculos')
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('lista_vehiculos')
    return render(request, 'core/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ---------- Alquiler ----------
@login_required
def lista_alquileres(request):
    alquileres = Alquiler.objects.all()
    return render(request, 'core/lista_alquileres.html', {'alquileres': alquileres})

@login_required
def agregar_alquiler(request):
    form = AlquilerForm(request.POST or None)
    if form.is_valid():
        alquiler = form.save(commit=False)
        if alquiler.vehiculo.estado == 'disponible':
            alquiler.save()
            alquiler.vehiculo.estado = 'alquilado'
            alquiler.vehiculo.save()
            return redirect('lista_alquileres')
        else:
            form.add_error(None, "El vehículo no está disponible.")
    return render(request, 'core/agregar_alquiler.html', {'form': form})

@login_required
def devolver_alquiler(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    if request.method == 'POST':
        alquiler.vehiculo.estado = 'disponible'
        alquiler.vehiculo.save()
        alquiler.delete()
        return redirect('lista_alquileres')
    return render(request, 'core/devolver_alquiler.html', {'alquiler': alquiler})

# ---------- Mantenimiento ----------
@login_required
def lista_mantenimientos(request):
    filtros = {
        'vehiculo__patente__icontains': request.GET.get('patente', ''),
        'taller__nombre__icontains': request.GET.get('taller', ''),
        'fecha_ingreso__gte': request.GET.get('fecha_inicio', ''),
        'fecha_fin__lte': request.GET.get('fecha_fin', ''),
        'estado': request.GET.get('estado', ''),
    }
    filtros = {k: v for k, v in filtros.items() if v}
    mantenimientos = Mantenimiento.objects.filter(**filtros)
    return render(request, 'core/lista_mantenimientos.html', {
        'mantenimientos': mantenimientos,
        **request.GET.dict()
    })

@login_required
def agregar_mantenimiento(request):
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        formset_lineas = LineaTrabajoFormSet(request.POST, prefix='lineas')
        formset_usados = RepuestoUsadoFormSet(request.POST, prefix='usados')
        formset_libres = RepuestoUtilizadoFormSet(request.POST, prefix='libres')
        formset_documentos = DocumentoFormSet(request.POST, request.FILES, prefix='documentos')
        if form.is_valid() and formset_lineas.is_valid() and formset_usados.is_valid() and formset_libres.is_valid() and formset_documentos.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.encargado = request.user
            mantenimiento.save()
            # Guardar formsets
            for fs in [formset_lineas, formset_usados, formset_libres, formset_documentos]:
                fs.instance = mantenimiento
                fs.save()
            return redirect('lista_mantenimientos')
    else:
        form = MantenimientoForm()
        formset_lineas = LineaTrabajoFormSet(prefix='lineas')
        formset_usados = RepuestoUsadoFormSet(prefix='usados')
        formset_libres = RepuestoUtilizadoFormSet(prefix='libres')
        formset_documentos = DocumentoFormSet(prefix='documentos')
    return render(request, 'core/agregar_mantenimiento.html', {
        'form': form,
        'formset_lineas': formset_lineas,
        'formset_usados': formset_usados,
        'formset_libres': formset_libres,
        'formset_documentos': formset_documentos,
    })

@login_required
def editar_mantenimiento(request, pk):
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        formset_lineas = LineaTrabajoFormSet(request.POST, instance=mantenimiento, prefix='lineas')
        formset_usados = RepuestoUsadoFormSet(request.POST, instance=mantenimiento, prefix='usados')
        formset_libres = RepuestoUtilizadoFormSet(request.POST, instance=mantenimiento, prefix='libres')
        formset_documentos = DocumentoFormSet(request.POST, request.FILES, instance=mantenimiento, prefix='documentos')
        if form.is_valid() and formset_lineas.is_valid() and formset_usados.is_valid() and formset_libres.is_valid() and formset_documentos.is_valid():
            form.save()
            for fs in [formset_lineas, formset_usados, formset_libres, formset_documentos]:
                fs.save()
            return redirect('lista_mantenimientos')
    else:
        form = MantenimientoForm(instance=mantenimiento)
        formset_lineas = LineaTrabajoFormSet(instance=mantenimiento, prefix='lineas')
        formset_usados = RepuestoUsadoFormSet(instance=mantenimiento, prefix='usados')
        formset_libres = RepuestoUtilizadoFormSet(instance=mantenimiento, prefix='libres')
        formset_documentos = DocumentoFormSet(instance=mantenimiento, prefix='documentos')
    return render(request, 'core/editar_mantenimiento.html', {
        'form': form,
        'formset_lineas': formset_lineas,
        'formset_usados': formset_usados,
        'formset_libres': formset_libres,
        'formset_documentos': formset_documentos,
        'mantenimiento': mantenimiento,
    })

@login_required
def eliminar_mantenimiento(request, pk):
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == 'POST':
        mantenimiento.delete()
        return redirect('lista_mantenimientos')
    return render(request, 'core/eliminar_mantenimiento.html', {'mantenimiento': mantenimiento})
