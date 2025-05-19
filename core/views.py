from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Vehiculo, Alquiler, Mantenimiento
from .forms import VehiculoForm, AlquilerForm, MantenimientoForm, LineaTrabajoFormSet

@login_required
def lista_vehiculos(request):
    print("Entrando a lista_vehiculos")
    print(f"Usuario autenticado: {request.user.is_authenticated}")
    print(f"Usuario: {request.user}")
    vehiculos = Vehiculo.objects.all()
    print(f"Vehículos encontrados: {vehiculos}")
    return render(request, 'core/lista_vehiculos.html', {'vehiculos': vehiculos})

@login_required
def agregar_vehiculo(request):
    print("Entrando a agregar_vehiculo")
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vehiculos')
    else:
        form = VehiculoForm()
    print("Renderizando agregar_vehiculo.html")
    return render(request, 'core/agregar_vehiculo.html', {'form': form})

@login_required
def detalle_vehiculo(request, pk):
    print(f"Entrando a detalle_vehiculo con pk={pk}")
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    print(f"Vehículo encontrado: {vehiculo}")
    return render(request, 'core/detalle_vehiculo.html', {'vehiculo': vehiculo})

@login_required
def editar_vehiculo(request, pk):
    print(f"Entrando a editar_vehiculo con pk={pk}")
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    print(f"Vehículo encontrado: {vehiculo}")
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            return redirect('lista_vehiculos')
    else:
        form = VehiculoForm(instance=vehiculo)
        print(f"Formulario creado: {form}")
    print("Renderizando editar_vehiculo.html")
    return render(request, 'core/editar_vehiculo.html', {'form': form, 'vehiculo': vehiculo})

@login_required
def eliminar_vehiculo(request, pk):
    print(f"Entrando a eliminar_vehiculo con pk={pk}")
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    print(f"Vehículo encontrado: {vehiculo}")
    if request.method == 'POST':
        vehiculo.delete()
        return redirect('lista_vehiculos')
    print("Renderizando eliminar_vehiculo.html")
    return render(request, 'core/eliminar_vehiculo.html', {'vehiculo': vehiculo})

def login_view(request):
    print("Entrando a login_view")
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('lista_vehiculos')
    else:
        form = AuthenticationForm()
    print("Renderizando login.html")
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    print("Entrando a register_view")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_vehiculos')
    else:
        form = UserCreationForm()
    print("Renderizando register.html")
    return render(request, 'core/register.html', {'form': form})

@login_required
def logout_view(request):
    print("Entrando a logout_view")
    logout(request)
    return redirect('login')

@login_required
def lista_alquileres(request):
    print("Entrando a lista_alquileres")
    alquileres = Alquiler.objects.all()
    print(f"Alquileres encontrados: {alquileres}")
    print(f"Número de alquileres: {alquileres.count()}")
    return render(request, 'core/lista_alquileres.html', {'alquileres': alquileres})

@login_required
def agregar_alquiler(request):
    print("Entrando a agregar_alquiler")
    try:
        if request.method == 'POST':
            form = AlquilerForm(request.POST)
            if form.is_valid():
                alquiler = form.save(commit=False)
                if alquiler.vehiculo.estado == 'disponible':
                    alquiler.costo_total = 50.00
                    alquiler.save()
                    alquiler.vehiculo.estado = 'alquilado'
                    alquiler.vehiculo.save()
                    print("Alquiler guardado con éxito")
                    return redirect('lista_alquileres')
                else:
                    form.add_error(None, "El vehículo no está disponible para alquiler.")
                    print("Error: Vehículo no disponible")
            else:
                print(f"Errores en el formulario: {form.errors}")
        else:
            form = AlquilerForm()
            print("Formulario creado para GET")
            print(f"Formulario: {form}")
        print("Renderizando agregar_alquiler.html")
        context = {'form': form}
        print(f"Contexto enviado a la plantilla: {context}")
        return render(request, 'core/agregar_alquiler.html', context)
    except Exception as e:
        print(f"Error en agregar_alquiler: {str(e)}")
        return render(request, 'core/agregar_alquiler.html', {'error': f"Error: {str(e)}"})
    
@login_required
def devolver_alquiler(request, pk):
    print(f"Entrando a devolver_alquiler con pk={pk}")
    alquiler = get_object_or_404(Alquiler, pk=pk)
    if request.method == 'POST':
        alquiler.vehiculo.estado = 'disponible'
        alquiler.vehiculo.save()
        alquiler.delete()
        print("Alquiler devuelto y eliminado con éxito")
        return redirect('lista_alquileres')
    print("Renderizando devolver_alquiler.html")
    return render(request, 'core/devolver_alquiler.html', {'alquiler': alquiler})

@login_required
def lista_mantenimientos(request):
    print("Entrando a lista_mantenimientos")
    mantenimientos = Mantenimiento.objects.all()
    print(f"Mantenimientos encontrados: {mantenimientos}")
    return render(request, 'core/lista_mantenimientos.html', {'mantenimientos': mantenimientos})

@login_required
def agregar_mantenimiento(request):
    print("Entrando a agregar_mantenimiento")
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        formset = LineaTrabajoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            mantenimiento = form.save()
            formset.instance = mantenimiento
            formset.save()
            print(f"Mantenimiento guardado: {mantenimiento}")
            return redirect('lista_mantenimientos')
    else:
        form = MantenimientoForm()
        formset = LineaTrabajoFormSet()
    return render(request, 'core/agregar_mantenimiento.html', {
        'form': form,
        'formset': formset
    })

@login_required
def editar_mantenimiento(request, pk):
    print("Entrando a editar_mantenimiento")
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        formset = LineaTrabajoFormSet(request.POST, instance=mantenimiento)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            print(f"Mantenimiento actualizado: {mantenimiento}")
            return redirect('lista_mantenimientos')
    else:
        form = MantenimientoForm(instance=mantenimiento)
        formset = LineaTrabajoFormSet(instance=mantenimiento)  # Eliminar extra=1 aquí
    return render(request, 'core/editar_mantenimiento.html', {
        'form': form,
        'formset': formset,
        'mantenimiento': mantenimiento
    })

@login_required
def eliminar_mantenimiento(request, pk):
    print("Entrando a eliminar_mantenimiento")
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == 'POST':
        print(f"Eliminando mantenimiento: {mantenimiento}")
        mantenimiento.delete()
        return redirect('lista_mantenimientos')
    return render(request, 'core/eliminar_mantenimiento.html', {'mantenimiento': mantenimiento})