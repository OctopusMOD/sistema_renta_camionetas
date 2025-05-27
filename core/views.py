from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone  # Añadido para manejar fechas
import time
from datetime import timedelta, date
from .models import Vehiculo, Alquiler, Mantenimiento, TrabajoRealizado, Repuesto, Producto, Proveedor, MovimientoInventario, Taller, Marca, Modelo, Cliente
from .forms import VehiculoForm, AlquilerForm, MantenimientoForm, TrabajoRealizadoFormSet, RepuestoFormSet, ProductoForm, ProveedorForm, IngresoArticuloForm, TallerForm, ClienteForm

# ---------- Vista Principal ----------
@login_required
def index(request):
    context = {'timestamp': int(time.time())}
    return render(request, 'core/index.html', context)

# ---------- Vehículos ----------
@login_required
def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    context = {'vehiculos': vehiculos, 'timestamp': int(time.time())}
    return render(request, 'core/lista_vehiculos.html', context)

@login_required
def agregar_vehiculo(request):
    if request.method == 'POST':
        try:
            patente = request.POST['patente'].strip()
            kilometraje = request.POST['kilometraje'].strip()
            marca_nombre = request.POST['marca'].strip()
            modelo_nombre = request.POST['modelo'].strip()
            anio = request.POST['anio'].strip()
            color = request.POST['color'].strip()
            vin = request.POST['vin'].strip()
            combustible = request.POST['combustible']
            transmision = request.POST['transmision']
            traccion = request.POST['traccion']
            capacidad_estanque = request.POST['capacidad_estanque'].strip()
            cilindrada = request.POST['cilindrada'].strip()
            capacidad_carga = request.POST['capacidad_carga'].strip()
            permiso_circulacion = request.POST['permiso_circulacion']
            soap = request.POST['soap']
            revision_tecnica = request.POST['revision_tecnica']

            if Vehiculo.objects.filter(patente=patente).exists():
                messages.error(request, "La placa patente ya está registrada.")
                return redirect('agregar_vehiculo')
            if vin and Vehiculo.objects.filter(vin=vin).exists():
                messages.error(request, "El VIN ya está registrado.")
                return redirect('agregar_vehiculo')
            if not kilometraje.isdigit() or not (0 <= int(kilometraje) <= 500000):
                messages.error(request, "El kilometraje debe estar entre 0 y 500,000.")
                return redirect('agregar_vehiculo')
            if len(color) > 20:
                messages.error(request, "El color no puede exceder los 20 caracteres.")
                return redirect('agregar_vehiculo')
            if len(vin) > 70:
                messages.error(request, "El VIN no puede exceder los 70 caracteres.")
                return redirect('agregar_vehiculo')
            if not anio.isdigit() or not (1900 <= int(anio) <= 2025):
                messages.error(request, "El año debe estar entre 1900 y 2025.")
                return redirect('agregar_vehiculo')
            if not patente or len(patente) > 10:
                messages.error(request, "La patente es requerida y no puede exceder los 10 caracteres.")
                return redirect('agregar_vehiculo')
            try:
                capacidad_estanque = float(capacidad_estanque)
                if capacidad_estanque <= 0:
                    messages.error(request, "La capacidad del estanque debe ser mayor a 0 litros.")
                    return redirect('agregar_vehiculo')
            except ValueError:
                messages.error(request, "La capacidad del estanque debe ser un número válido.")
                return redirect('agregar_vehiculo')
            try:
                cilindrada = float(cilindrada)
                if cilindrada <= 0:
                    messages.error(request, "La cilindrada debe ser mayor a 0 cc.")
                    return redirect('agregar_vehiculo')
            except ValueError:
                messages.error(request, "La cilindrada debe ser un número válido.")
                return redirect('agregar_vehiculo')
            try:
                capacidad_carga = float(capacidad_carga)
                if capacidad_carga <= 0:
                    messages.error(request, "La capacidad de carga debe ser mayor a 0 kg.")
                    return redirect('agregar_vehiculo')
            except ValueError:
                messages.error(request, "La capacidad de carga debe ser un número válido.")
                return redirect('agregar_vehiculo')

            marca, created = Marca.objects.get_or_create(nombre=marca_nombre)
            if created and not modelo_nombre:
                messages.error(request, "Debe ingresar un modelo al crear una nueva marca.")
                return redirect('agregar_vehiculo')
            elif created:
                modelo, _ = Modelo.objects.get_or_create(marca=marca, nombre=modelo_nombre)
            else:
                modelo, created_modelo = Modelo.objects.get_or_create(marca=marca, nombre=modelo_nombre)

            vehiculo = Vehiculo(
                patente=patente,
                kilometraje=int(kilometraje),
                marca=marca,
                modelo=modelo,
                anio=int(anio),
                color=color,
                vin=vin,
                combustible=combustible,
                transmision=transmision,
                traccion=traccion,
                capacidad_estanque=capacidad_estanque,
                cilindrada=cilindrada,
                capacidad_carga=capacidad_carga,
                permiso_circulacion=permiso_circulacion,
                soap=soap,
                revision_tecnica=revision_tecnica
            )
            vehiculo.save()
            messages.success(request, "Vehículo agregado exitosamente.")
            return redirect('lista_vehiculos')
        except Exception as e:
            messages.error(request, f"Error al agregar el vehículo: {str(e)}")
            return redirect('agregar_vehiculo')
    context = {
        'marcas': Marca.objects.all(),
        'modelos': Modelo.objects.all(),
        'timestamp': int(time.time())
    }
    return render(request, 'core/agregar_vehiculo.html', context)

@login_required
def detalle_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    context = {'vehiculo': vehiculo, 'timestamp': int(time.time())}
    return render(request, 'core/detalle_vehiculo.html', context)

@login_required
def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == 'POST':
        try:
            patente = request.POST['patente'].strip()
            kilometraje = request.POST['kilometraje'].strip()
            marca_nombre = request.POST['marca'].strip()
            modelo_nombre = request.POST['modelo'].strip()
            anio = request.POST['anio'].strip()
            color = request.POST['color'].strip()
            vin = request.POST['vin'].strip()
            combustible = request.POST['combustible']
            transmision = request.POST['transmision']
            traccion = request.POST['traccion']
            capacidad_estanque = request.POST['capacidad_estanque'].strip()
            cilindrada = request.POST['cilindrada'].strip()
            capacidad_carga = request.POST['capacidad_carga'].strip()
            permiso_circulacion = request.POST['permiso_circulacion']
            soap = request.POST['soap']
            revision_tecnica = request.POST['revision_tecnica']

            if Vehiculo.objects.filter(patente=patente).exclude(pk=pk).exists():
                messages.error(request, "La placa patente ya está registrada.")
                return redirect('editar_vehiculo', pk=pk)
            if vin and Vehiculo.objects.filter(vin=vin).exclude(pk=pk).exists():
                messages.error(request, "El VIN ya está registrado.")
                return redirect('editar_vehiculo', pk=pk)
            if not kilometraje.isdigit() or not (0 <= int(kilometraje) <= 500000):
                messages.error(request, "El kilometraje debe estar entre 0 y 500,000.")
                return redirect('editar_vehiculo', pk=pk)
            if len(color) > 20:
                messages.error(request, "El color no puede exceder los 20 caracteres.")
                return redirect('editar_vehiculo', pk=pk)
            if len(vin) > 70:
                messages.error(request, "El VIN no puede exceder los 70 caracteres.")
                return redirect('editar_vehiculo', pk=pk)
            if not anio.isdigit() or not (1900 <= int(anio) <= 2025):
                messages.error(request, "El año debe estar entre 1900 y 2025.")
                return redirect('editar_vehiculo', pk=pk)
            if not patente or len(patente) > 10:
                messages.error(request, "La patente es requerida y no puede exceder los 10 caracteres.")
                return redirect('editar_vehiculo', pk=pk)
            try:
                capacidad_estanque = float(capacidad_estanque)
                if capacidad_estanque <= 0:
                    messages.error(request, "La capacidad del estanque debe ser mayor a 0 litros.")
                    return redirect('editar_vehiculo', pk=pk)
            except ValueError:
                messages.error(request, "La capacidad del estanque debe ser un número válido.")
                return redirect('editar_vehiculo', pk=pk)
            try:
                cilindrada = float(cilindrada)
                if cilindrada <= 0:
                    messages.error(request, "La cilindrada debe ser mayor a 0 cc.")
                    return redirect('editar_vehiculo', pk=pk)
            except ValueError:
                messages.error(request, "La cilindrada debe ser un número válido.")
                return redirect('editar_vehiculo', pk=pk)
            try:
                capacidad_carga = float(capacidad_carga)
                if capacidad_carga <= 0:
                    messages.error(request, "La capacidad de carga debe ser mayor a 0 kg.")
                    return redirect('editar_vehiculo', pk=pk)
            except ValueError:
                messages.error(request, "La capacidad de carga debe ser un número válido.")
                return redirect('editar_vehiculo', pk=pk)

            marca, _ = Marca.objects.get_or_create(nombre=marca_nombre)
            if not modelo_nombre:
                messages.error(request, "Debe ingresar un modelo.")
                return redirect('editar_vehiculo', pk=pk)
            modelo, _ = Modelo.objects.get_or_create(marca=marca, nombre=modelo_nombre)

            vehiculo.patente = patente
            vehiculo.kilometraje = int(kilometraje)
            vehiculo.marca = marca
            vehiculo.modelo = modelo
            vehiculo.anio = int(anio)
            vehiculo.color = color
            vehiculo.vin = vin
            vehiculo.combustible = combustible
            vehiculo.transmision = transmision
            vehiculo.traccion = traccion
            vehiculo.capacidad_estanque = capacidad_estanque
            vehiculo.cilindrada = cilindrada
            vehiculo.capacidad_carga = capacidad_carga
            vehiculo.permiso_circulacion = permiso_circulacion
            vehiculo.soap = soap
            vehiculo.revision_tecnica = revision_tecnica
            vehiculo.save()
            messages.success(request, "Vehículo actualizado exitosamente.")
            return redirect('lista_vehiculos')
        except Exception as e:
            messages.error(request, f"Error al actualizar el vehículo: {str(e)}")
            return redirect('editar_vehiculo', pk=pk)
    context = {
        'vehiculo': vehiculo,
        'marcas': Marca.objects.all(),
        'modelos': Modelo.objects.all(),
        'timestamp': int(time.time())
    }
    return render(request, 'core/editar_vehiculo.html', context)

@login_required
def eliminar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == 'POST':
        vehiculo.delete()
        messages.success(request, "Vehículo eliminado exitosamente.")
        return redirect('lista_vehiculos')
    context = {'vehiculo': vehiculo, 'timestamp': int(time.time())}
    return render(request, 'core/eliminar_vehiculo.html', context)

@login_required
def lista_flota_activa(request):
    vehiculos_activos = Vehiculo.objects.filter(estado='disponible')
    context = {'vehiculos': vehiculos_activos, 'timestamp': int(time.time())}
    return render(request, 'core/lista_flota_activa.html', context)

@login_required
def gestion_categorias(request):
    context = {'message': 'Gestión de Categorías en construcción', 'timestamp': int(time.time())}
    return render(request, 'core/gestion_categorias.html', context)

# ---------- Autenticación ----------
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect('index')
    else:
        form = AuthenticationForm()
    context = {'form': form, 'timestamp': int(time.time())}
    return render(request, 'core/login.html', context)

def register_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Usuario registrado exitosamente.")
        return redirect('index')
    context = {'form': form, 'timestamp': int(time.time())}
    return render(request, 'core/register.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('login')

# ---------- Clientes ----------
@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente {cliente.nombre or cliente.razon_social} agregado exitosamente.")
            return redirect('lista_alquileres')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = ClienteForm()
    context = {'form': form, 'timestamp': int(time.time())}
    return render(request, 'core/agregar_cliente.html', context)

# ---------- Alquileres ----------
@login_required
def lista_alquileres(request):
    alquileres = Alquiler.objects.all()
    context = {'alquileres': alquileres, 'timestamp': int(time.time())}
    return render(request, 'core/lista_alquileres.html', context)

@login_required
def agregar_alquiler(request):
    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        if form.is_valid():
            alquiler = form.save(commit=False)
            alquiler.nivel_combustible_entrega = request.POST.get('nivel_combustible_entrega', 'N/A')
            alquiler.creado_por = request.user
            alquiler.save()
            alquiler.vehiculo.estado = 'alquilado'
            alquiler.vehiculo.save()
            messages.success(request, f"Alquiler registrado exitosamente. Contrato N° {alquiler.numero_alquiler}")
            return redirect('lista_alquileres')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = AlquilerForm()
    # Añadir today al contexto y otras variables necesarias
    today = timezone.now().date()
    context = {
        'form': form,
        'timestamp': int(time.time()),
        'today': today,  # Añadido para resolver el error
        'alquileres': Alquiler.objects.all(),  # Para alquileres.count en la plantilla
        'alquiler': Alquiler() if not form.instance.pk else form.instance,  # Objeto vacío o existente
    }
    return render(request, 'core/agregar_alquiler.html', context)

@login_required
def editar_alquiler(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    if request.method == 'POST':
        form = AlquilerForm(request.POST, instance=alquiler)
        if form.is_valid():
            form.save()
            messages.success(request, f"Alquiler actualizado exitosamente. Contrato N° {alquiler.numero_alquiler}")
            return redirect('lista_alquileres')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = AlquilerForm(instance=alquiler)
    # Añadir today al contexto y otras variables necesarias
    today = timezone.now().date()
    context = {
        'form': form,
        'timestamp': int(time.time()),
        'today': today,  # Añadido para la plantilla
        'alquileres': Alquiler.objects.all(),  # Para alquileres.count
        'alquiler': alquiler,  # Objeto existente
    }
    return render(request, 'core/agregar_alquiler.html', context)

@login_required
def devolver_alquiler(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    if request.method == 'POST':
        kilometraje_fin = request.POST.get('kilometraje_fin')
        nivel_combustible_devolucion = request.POST.get('nivel_combustible_devolucion', 'N/A')
        try:
            kilometraje_fin = int(kilometraje_fin)
            if kilometraje_fin < alquiler.vehiculo.kilometraje:
                messages.error(request, "El kilometraje final no puede ser menor al kilometraje inicial.")
                return redirect('devolver_alquiler', pk=pk)
            alquiler.vehiculo.kilometraje = kilometraje_fin
            alquiler.vehiculo.estado = 'disponible'
            alquiler.vehiculo.save()
            alquiler.estado = 'completado'
            alquiler.nivel_combustible_devolucion = nivel_combustible_devolucion
            alquiler.fecha_termino = date.today()
            alquiler.save()
            messages.success(request, f"Alquiler devuelto exitosamente. Contrato N° {alquiler.numero_alquiler}")
            return redirect('lista_alquileres')
        except ValueError:
            messages.error(request, "El kilometraje final debe ser un número válido.")
            return redirect('devolver_alquiler', pk=pk)
    context = {'alquiler': alquiler, 'timestamp': int(time.time())}
    return render(request, 'core/devolver_alquiler.html', context)

@login_required
def eliminar_alquiler(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    if request.method == 'POST':
        if alquiler.estado == 'activo':
            alquiler.vehiculo.estado = 'disponible'
            alquiler.vehiculo.save()
        alquiler.delete()
        messages.success(request, "Alquiler eliminado exitosamente.")
        return redirect('lista_alquileres')
    context = {'alquiler': alquiler, 'timestamp': int(time.time())}
    return render(request, 'core/eliminar_alquiler.html', context)

# ---------- Mantenimientos ----------
@login_required
def lista_mantenimientos(request):
    filtros = {
        'vehiculo__patente__icontains': request.GET.get('patente', ''),
        'taller__nombre_comercial__icontains': request.GET.get('taller', ''),
        'fecha_ingreso__gte': request.GET.get('fecha_inicio', ''),
        'fecha_salida__lte': request.GET.get('fecha_fin', ''),
        'confirmado': request.GET.get('confirmado', ''),
        'observaciones__icontains': request.GET.get('observaciones', ''),
    }
    filtros = {k: v for k, v in filtros.items() if v not in ['', None]}

    if 'confirmado' in filtros:
        if filtros['confirmado'].lower() == 'true':
            filtros['confirmado'] = True
        elif filtros['confirmado'].lower() == 'false':
            filtros['confirmado'] = False
        else:
            del filtros['confirmado']

    if 'confirmado' not in filtros:
        filtros['confirmado'] = False

    mantenimientos = Mantenimiento.objects.filter(**filtros).order_by('-fecha_ingreso')
    context = {
        'mantenimientos': mantenimientos,
        'query_patente': request.GET.get('patente', ''),
        'query_taller': request.GET.get('taller', ''),
        'query_fecha_inicio': request.GET.get('fecha_inicio', ''),
        'query_fecha_fin': request.GET.get('fecha_fin', ''),
        'query_confirmado': request.GET.get('confirmado', ''),
        'query_observaciones': request.GET.get('observaciones', ''),
        'timestamp': int(time.time()),
    }
    return render(request, 'core/lista_mantenimientos.html', context)

@login_required
def agregar_mantenimiento(request):
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        trabajo_formset = TrabajoRealizadoFormSet(request.POST, prefix='trabajos')
        repuesto_formset = RepuestoFormSet(request.POST, prefix='repuestos')

        if form.is_valid() and trabajo_formset.is_valid() and repuesto_formset.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.creado_por = request.user
            mantenimiento.encargado = request.user.username
            if mantenimiento.vehiculo.estado == 'disponible':
                mantenimiento.vehiculo.estado = 'mantenimiento'
                mantenimiento.vehiculo.save()
            mantenimiento.save()

            trabajos = trabajo_formset.save(commit=False)
            for trabajo in trabajos:
                trabajo.mantenimiento = mantenimiento
                trabajo.save()
            for obj in trabajo_formset.deleted_objects:
                obj.delete()

            repuestos = repuesto_formset.save(commit=False)
            for repuesto in repuestos:
                repuesto.mantenimiento = mantenimiento
                if repuesto.producto:
                    if repuesto.producto.unidades >= repuesto.unidades:
                        repuesto.producto.unidades -= repuesto.unidades
                        repuesto.producto.save()
                        MovimientoInventario.objects.create(
                            producto=repuesto.producto,
                            tipo='Salida',
                            cantidad=repuesto.unidades,
                            usuario=request.user,
                            mantenimiento=mantenimiento,
                            notas=f"Salida por mantenimiento #{mantenimiento.id}"
                        )
                    else:
                        messages.error(request, f"No hay suficiente stock para el repuesto '{repuesto.producto.nombre}'. Stock disponible: {repuesto.producto.unidades}.")
                        mantenimiento.delete()
                        return redirect('agregar_mantenimiento')
                repuesto.save()
            for obj in repuesto_formset.deleted_objects:
                if obj.producto:
                    obj.producto.unidades += obj.unidades
                    obj.producto.save()
                    MovimientoInventario.objects.create(
                        producto=obj.producto,
                        tipo='Ingreso',
                        cantidad=obj.unidades,
                        usuario=request.user,
                        notas=f"Reversión por eliminación de repuesto en mantenimiento #{mantenimiento.id}"
                    )
                obj.delete()

            messages.success(request, f"Mantenimiento agregado exitosamente. ODT {mantenimiento.id}")
            return redirect('lista_mantenimientos')
    else:
        form = MantenimientoForm()
        trabajo_formset = TrabajoRealizadoFormSet(prefix='trabajos')
        repuesto_formset = RepuestoFormSet(prefix='repuestos')

    context = {
        'form': form,
        'trabajo_formset': trabajo_formset,
        'repuesto_formset': repuesto_formset,
        'timestamp': int(time.time())
    }
    return render(request, 'core/agregar_mantenimiento.html', context)

@login_required
def editar_mantenimiento(request, pk):
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    if mantenimiento.confirmado:
        messages.error(request, "No se puede editar un mantenimiento confirmado.")
        return redirect('lista_mantenimientos')

    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        trabajo_formset = TrabajoRealizadoFormSet(request.POST, instance=mantenimiento, prefix='trabajos')
        repuesto_formset = RepuestoFormSet(request.POST, instance=mantenimiento, prefix='repuestos')

        if form.is_valid() and trabajo_formset.is_valid() and repuesto_formset.is_valid():
            form.save()
            trabajos = trabajo_formset.save(commit=False)
            for trabajo in trabajos:
                trabajo.mantenimiento = mantenimiento
                trabajo.save()
            for obj in trabajo_formset.deleted_objects:
                obj.delete()

            repuestos = repuesto_formset.save(commit=False)
            for repuesto in repuestos:
                repuesto.mantenimiento = mantenimiento
                if repuesto.producto:
                    if repuesto.producto.unidades >= repuesto.unidades:
                        repuesto.producto.unidades -= repuesto.unidades
                        repuesto.producto.save()
                        MovimientoInventario.objects.create(
                            producto=repuesto.producto,
                            tipo='Salida',
                            cantidad=repuesto.unidades,
                            usuario=request.user,
                            mantenimiento=mantenimiento,
                            notas=f"Salida por edición de mantenimiento #{mantenimiento.id}"
                        )
                    else:
                        messages.error(request, f"No hay suficiente stock para el repuesto '{repuesto.producto.nombre}'. Stock disponible: {repuesto.producto.unidades}.")
                        return redirect('editar_mantenimiento', pk=pk)
                repuesto.save()
            for obj in repuesto_formset.deleted_objects:
                if obj.producto:
                    obj.producto.unidades += obj.unidades
                    obj.producto.save()
                    MovimientoInventario.objects.create(
                        producto=obj.producto,
                        tipo='Ingreso',
                        cantidad=obj.unidades,
                        usuario=request.user,
                        notas=f"Reversión por eliminación de repuesto en edición de mantenimiento #{mantenimiento.id}"
                    )
                obj.delete()

            messages.success(request, f"Mantenimiento actualizado exitosamente. ODT {mantenimiento.id}")
            return redirect('lista_mantenimientos')
    else:
        form = MantenimientoForm(instance=mantenimiento)
        trabajo_formset = TrabajoRealizadoFormSet(instance=mantenimiento, prefix='trabajos')
        repuesto_formset = RepuestoFormSet(instance=mantenimiento, prefix='repuestos')

    context = {
        'form': form,
        'trabajo_formset': trabajo_formset,
        'repuesto_formset': repuesto_formset,
        'mantenimiento': mantenimiento,
        'timestamp': int(time.time())
    }
    return render(request, 'core/editar_mantenimiento.html', context)

@login_required
def eliminar_mantenimiento(request, pk):
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    if request.method == 'POST':
        for repuesto in mantenimiento.repuestos.all():
            if repuesto.producto:
                repuesto.producto.unidades += repuesto.unidades
                repuesto.producto.save()
                MovimientoInventario.objects.create(
                    producto=repuesto.producto,
                    tipo='Ingreso',
                    cantidad=repuesto.unidades,
                    usuario=request.user,
                    notas=f"Reversión por eliminación de mantenimiento #{mantenimiento.id}"
                )
        if not mantenimiento.confirmado:
            mantenimiento.vehiculo.estado = 'disponible'
            mantenimiento.vehiculo.save()
        mantenimiento.delete()
        messages.success(request, "Mantenimiento eliminado exitosamente.")
        return redirect('lista_mantenimientos')
    context = {'mantenimiento': mantenimiento, 'timestamp': int(time.time())}
    return render(request, 'core/eliminar_mantenimiento.html', context)

# ---------- Talleres ----------
@login_required
def lista_talleres(request):
    talleres = Taller.objects.all()
    context = {'talleres': talleres, 'timestamp': int(time.time())}
    return render(request, 'core/lista_talleres.html', context)

@login_required
def gestionar_talleres(request):
    if request.method == 'POST':
        form = TallerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Taller agregado exitosamente.")
            return redirect('lista_talleres')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = TallerForm()
    context = {
        'form': form,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/gestionar_talleres.html', context)

@login_required
def editar_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk)
    if request.method == 'POST':
        form = TallerForm(request.POST, instance=taller)
        if form.is_valid():
            form.save()
            messages.success(request, "Taller actualizado exitosamente.")
            return redirect('lista_talleres')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = TallerForm(instance=taller)
    context = {'form': form, 'taller': taller, 'timestamp': int(time.time())}
    return render(request, 'core/editar_taller.html', context)

@login_required
def eliminar_taller(request, pk):
    taller = get_object_or_404(Taller, pk=pk)
    if request.method == 'POST':
        taller.delete()
        messages.success(request, "Taller eliminado exitosamente.")
        return redirect('lista_talleres')
    context = {'taller': taller, 'timestamp': int(time.time())}
    return render(request, 'core/eliminar_taller.html', context)

# ---------- Utilidades ----------
def test_form(request):
    form = MantenimientoForm()
    context = {'form': form, 'timestamp': int(time.time())}
    return render(request, 'core/test_form.html', context)

def check_patente(request):
    patente = request.GET.get('patente', '').strip()
    try:
        vehiculo = Vehiculo.objects.get(patente=patente)
        data = {
            'exists': True,
            'marca': vehiculo.marca.nombre if vehiculo.marca else '',
            'modelo': vehiculo.modelo.nombre if vehiculo.modelo else '',
            'traccion': vehiculo.traccion,
            'anio': vehiculo.anio,
            'vin': vehiculo.vin,
            'kilometraje': vehiculo.kilometraje
        }
    except Vehiculo.DoesNotExist:
        data = {'exists': False}
    return JsonResponse(data)

def check_codigo_trabajo(request):
    codigo = request.GET.get('codigo', '').strip()
    try:
        producto = Producto.objects.get(codigo_referencia=codigo)
        data = {
            'exists': True,
            'descripcion': producto.descripcion or '',
            'valor_unitario': float(producto.valor_unitario),
        }
    except Producto.DoesNotExist:
        data = {'exists': False}
    return JsonResponse(data)

def check_codigo_repuesto(request):
    codigo = request.GET.get('codigo', '').strip()
    try:
        producto = Producto.objects.get(codigo_referencia=codigo)
        data = {
            'exists': True,
            'articulo': producto.nombre,
            'valor_unitario': float(producto.valor_unitario),
            'stock': producto.unidades,
        }
    except Producto.DoesNotExist:
        data = {'exists': False}
    return JsonResponse(data)

def check_stock(request):
    codigo = request.GET.get('codigo', '').strip()
    unidades = request.GET.get('unidades', '1')
    try:
        unidades = int(unidades)
        if unidades <= 0:
            return JsonResponse({'valid': False, 'message': 'Las unidades deben ser mayores a 0.'})
        producto = Producto.objects.get(codigo_referencia=codigo)
        if producto.unidades < unidades:
            return JsonResponse({
                'valid': False,
                'message': f"No hay suficiente stock para el repuesto '{producto.nombre}'. Stock disponible: {producto.unidades}."
            })
        return JsonResponse({'valid': True})
    except (Producto.DoesNotExist, ValueError):
        return JsonResponse({'valid': False, 'message': 'Producto no encontrado o unidades inválidas.'})

# ---------- Bodega ----------
@login_required
def bodega(request):
    productos = Producto.objects.all()
    proveedores = Proveedor.objects.all()
    context = {
        'productos': productos,
        'proveedores': proveedores,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/bodega.html', context)

@login_required
def ingreso_articulos(request):
    if request.method == 'POST':
        form = IngresoArticuloForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.tipo = 'Ingreso'
            movimiento.usuario = request.user
            movimiento.save()
            movimiento.producto.unidades += movimiento.cantidad
            movimiento.producto.save()
            messages.success(request, "Artículos ingresados exitosamente.")
            return redirect('bodega')
    else:
        form = IngresoArticuloForm()

    context = {
        'form': form,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/ingreso_articulos.html', context)

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado exitosamente.")
            return redirect('bodega')
    else:
        form = ProductoForm(instance=producto)
    context = {
        'form': form,
        'producto': producto,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/editar_producto.html', context)

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado exitosamente.")
        return redirect('bodega')
    context = {
        'producto': producto,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/eliminar_producto.html', context)

@login_required
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    context = {
        'proveedores': proveedores,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/lista_proveedores.html', context)

@login_required
def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor agregado exitosamente.")
            return redirect('lista_proveedores')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = ProveedorForm()
    context = {
        'form': form,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/agregar_proveedor.html', context)

@login_required
def buscar_producto(request):
    codigo = request.GET.get('codigo', '').strip()
    nombre = request.GET.get('nombre', '').strip()

    if codigo:
        producto = Producto.objects.filter(codigo_referencia=codigo).first()
    elif nombre:
        producto = Producto.objects.filter(nombre__icontains=nombre).first()
    else:
        return JsonResponse({'exists': False})

    if producto:
        return JsonResponse({
            'exists': True,
            'codigo': producto.codigo_referencia,
            'nombre': producto.nombre,
            'categoria': producto.categoria,
            'valor_unitario': float(producto.valor_unitario),
        })
    return JsonResponse({'exists': False})

# ---------- Alertas ----------
@login_required
def alertas(request):
    today = date.today()
    warning_threshold = today + timedelta(days=7)

    vehiculos = Vehiculo.objects.all()
    alertas_documentos = []
    for vehiculo in vehiculos:
        if vehiculo.permiso_circulacion < today:
            alertas_documentos.append({
                'vehiculo': vehiculo,
                'tipo': 'Permiso de Circulación',
                'fecha_vencimiento': vehiculo.permiso_circulacion,
                'estado': 'Vencido'
            })
        elif vehiculo.permiso_circulacion <= warning_threshold:
            alertas_documentos.append({
                'vehiculo': vehiculo,
                'tipo': 'Permiso de Circulación',
                'fecha_vencimiento': vehiculo.permiso_circulacion,
                'estado': 'Próximo a vencer'
            })

        if vehiculo.soap < today:
            alertas_documentos.append({
                'vehiculo': vehiculo,
                'tipo': 'SOAP',
                'fecha_vencimiento': vehiculo.soap,
                'estado': 'Vencido'
            })
        elif vehiculo.soap <= warning_threshold:
            alertas_documentos.append({
                'vehiculo': vehiculo,
                'tipo': 'SOAP',
                'fecha_vencimiento': vehiculo.soap,
                'estado': 'Próximo a vencer'
            })

        if vehiculo.revision_tecnica < today:
            alertas_documentos.append({
                'vehiculo': vehiculo,
                'tipo': 'Revisión Técnica',
                'fecha_vencimiento': vehiculo.revision_tecnica,
                'estado': 'Vencido'
            })
        elif vehiculo.revision_tecnica <= warning_threshold:
            alertas_documentos.append({
                'vehiculo': vehiculo,
                'tipo': 'Revisión Técnica',
                'fecha_vencimiento': vehiculo.revision_tecnica,
                'estado': 'Próximo a vencer'
            })

    mantenimientos = Mantenimiento.objects.filter(confirmado=False)
    alertas_mantenimientos = []
    for mantenimiento in mantenimientos:
        dias_en_mantenimiento = (today - mantenimiento.fecha_ingreso).days
        if dias_en_mantenimiento > 7:
            alertas_mantenimientos.append({
                'mantenimiento': mantenimiento,
                'dias': dias_en_mantenimiento,
                'fecha_ingreso': mantenimiento.fecha_ingreso
            })

    context = {
        'alertas_documentos': alertas_documentos,
        'alertas_mantenimientos': alertas_mantenimientos,
        'timestamp': int(time.time()),
    }
    return render(request, 'core/alertas.html', context)