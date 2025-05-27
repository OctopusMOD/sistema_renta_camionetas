from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone  # Añadido para manejar fechas
from .models import Vehiculo, Cliente, Alquiler, Mantenimiento, Taller, TrabajoRealizado, Repuesto, Producto, Proveedor, MovimientoInventario
import re
from django.core.exceptions import ValidationError

# Constantes para elecciones (deben coincidir con las definidas en models.py)
NIVEL_COMBUSTIBLE = [
    ('1/8', '1/8'),
    ('2/8', '2/8'),
    ('3/8', '3/8'),
    ('4/8', '4/8'),
    ('5/8', '5/8'),
    ('6/8', '6/8'),
    ('7/8', '7/8'),
    ('8/8', '8/8'),
    ('N/A', 'N/A'),
]

# Validación del RUT (formato chileno: 12.345.678-9 o 12345678-9)
def validar_rut(value):
    if not value:
        raise ValidationError("El RUT es obligatorio.")
    rut = value.replace('.', '').replace('-', '').upper()
    if not re.match(r'^\d{1,8}[0-9K]$', rut):
        raise ValidationError("El RUT debe tener un formato válido (ejemplo: 12.345.678-9 o 12345678-9).")
    cuerpo, dv = rut[:-1], rut[-1]
    suma = 0
    multiplo = 2
    for i in range(len(cuerpo) - 1, -1, -1):
        suma += int(cuerpo[i]) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    resto = suma % 11
    dv_esperado = 11 - resto
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)
    if dv != dv_esperado:
        raise ValidationError("El dígito verificador del RUT es incorrecto.")

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'anio', 'patente', 'estado']
        labels = {
            'marca': 'Marca',
            'modelo': 'Modelo',
            'anio': 'Año',
            'patente': 'Patente',
            'estado': 'Estado',
        }
        widgets = {
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.Select(attrs={'class': 'form-select'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'patente': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_cliente', 'rut', 'nombre', 'telefono', 'correo', 'direccion', 'licencia_conducir',
                  'razon_social', 'rut_empresa', 'contacto_principal', 'telefono_empresa', 'correo_empresa',
                  'giro', 'direccion_fiscal']
        widgets = {
            'tipo_cliente': forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleFields(this.value)'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej: Av. Siempre Viva 123, Santiago'}),
            'licencia_conducir': forms.TextInput(attrs={'class': 'form-control'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 76.543.210-5'}),
            'contacto_principal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56987654321'}),
            'correo_empresa': forms.EmailInput(attrs={'class': 'form-control'}),
            'giro': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_fiscal': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej: Av. Principal 456, Santiago'}),
        }
        labels = {
            'tipo_cliente': 'Tipo de Cliente',
            'rut': 'RUT',
            'nombre': 'Nombre Completo',
            'telefono': 'Teléfono',
            'correo': 'Correo Electrónico',
            'direccion': 'Dirección',
            'licencia_conducir': 'Licencia de Conducir',
            'razon_social': 'Razón Social',
            'rut_empresa': 'RUT Empresa',
            'contacto_principal': 'Contacto Principal',
            'telefono_empresa': 'Teléfono Empresa',
            'correo_empresa': 'Correo Electrónico Empresa',
            'giro': 'Giro',
            'direccion_fiscal': 'Dirección Fiscal',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicialmente ocultamos los campos de empresa
        self.fields['razon_social'].widget.attrs['class'] += ' d-none'
        self.fields['rut_empresa'].widget.attrs['class'] += ' d-none'
        self.fields['contacto_principal'].widget.attrs['class'] += ' d-none'
        self.fields['telefono_empresa'].widget.attrs['class'] += ' d-none'
        self.fields['correo_empresa'].widget.attrs['class'] += ' d-none'
        self.fields['giro'].widget.attrs['class'] += ' d-none'
        self.fields['direccion_fiscal'].widget.attrs['class'] += ' d-none'

    def clean(self):
        cleaned_data = super().clean()
        tipo_cliente = cleaned_data.get('tipo_cliente')

        if tipo_cliente == 'natural':
            if not all([cleaned_data.get('rut'), cleaned_data.get('nombre'), cleaned_data.get('telefono'),
                       cleaned_data.get('correo'), cleaned_data.get('licencia_conducir')]):
                raise ValidationError("Todos los campos de Persona Natural son obligatorios.")
            validar_rut(cleaned_data['rut'])
            if Cliente.objects.exclude(id=self.instance.id or None).filter(rut=cleaned_data['rut']).exists():
                raise ValidationError("El RUT ya está registrado.")
            if Cliente.objects.exclude(id=self.instance.id or None).filter(licencia_conducir=cleaned_data['licencia_conducir']).exists():
                raise ValidationError("La licencia de conducir ya está registrada.")
            # Limpiamos campos de empresa
            for field in ['razon_social', 'rut_empresa', 'contacto_principal', 'telefono_empresa',
                         'correo_empresa', 'giro', 'direccion_fiscal']:
                cleaned_data[field] = None
        elif tipo_cliente == 'empresa':
            if not all([cleaned_data.get('razon_social'), cleaned_data.get('rut_empresa'),
                       cleaned_data.get('contacto_principal'), cleaned_data.get('telefono_empresa'),
                       cleaned_data.get('correo_empresa'), cleaned_data.get('giro'),
                       cleaned_data.get('direccion_fiscal')]):
                raise ValidationError("Todos los campos de Empresa son obligatorios.")
            validar_rut(cleaned_data['rut_empresa'])
            if Cliente.objects.exclude(id=self.instance.id or None).filter(rut_empresa=cleaned_data['rut_empresa']).exists():
                raise ValidationError("El RUT de la empresa ya está registrado.")
            # Limpiamos campos de persona natural
            for field in ['rut', 'nombre', 'telefono', 'correo', 'licencia_conducir']:
                cleaned_data[field] = None

        return cleaned_data

class AlquilerForm(forms.ModelForm):
    tipo_alquiler = forms.ChoiceField(choices=Alquiler.TIPO_ALQUILER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    tipo_cliente = forms.ChoiceField(choices=Cliente.TIPO_CLIENTE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    rut = forms.CharField(max_length=12, required=False, label='RUT Cliente/Empresa')
    vehiculo_patente = forms.CharField(max_length=10, label='Patente Vehículo')

    class Meta:
        model = Alquiler
        fields = ['tipo_alquiler', 'tipo_cliente', 'rut', 'vehiculo_patente', 'fecha_inicio', 'fecha_termino', 'valor_diario', 'garantia', 'anotaciones_internas', 'anotaciones_publicas']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_termino': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_diario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'garantia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'anotaciones_internas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'anotaciones_publicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'tipo_alquiler': 'Tipo de Alquiler',
            'tipo_cliente': 'Tipo de Cliente',
            'rut': 'RUT Cliente/Empresa',
            'vehiculo_patente': 'Patente Vehículo',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_termino': 'Fecha de Término',
            'valor_diario': 'Valor Diario (CLP)',
            'garantia': 'Garantía (CLP)',
            'anotaciones_internas': 'Anotaciones Internas',
            'anotaciones_publicas': 'Anotaciones Públicas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rut'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'})
        self.fields['vehiculo_patente'].widget.attrs.update({'class': 'form-control'})
        # Establecer fecha_inicio como la fecha actual si es un nuevo alquiler
        if not self.instance.pk:  # Solo para nuevos alquileres
            self.initial['fecha_inicio'] = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        tipo_cliente = cleaned_data.get('tipo_cliente')
        rut = cleaned_data.get('rut')
        vehiculo_patente = cleaned_data.get('vehiculo_patente')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_termino = cleaned_data.get('fecha_termino')

        if not rut:
            raise ValidationError("El RUT es obligatorio.")
        validar_rut(rut)
        if not vehiculo_patente:
            raise ValidationError("La patente del vehículo es obligatoria.")
        if fecha_inicio and fecha_termino and fecha_inicio > fecha_termino:
            raise ValidationError("La fecha de término no puede ser anterior a la fecha de inicio.")
        
        # Buscar cliente o crear si no existe
        try:
            cliente = Cliente.objects.get(
                Q(rut=rut) | Q(rut_empresa=rut),
                tipo_cliente=tipo_cliente
            )
        except Cliente.DoesNotExist:
            raise ValidationError("Cliente no encontrado. Verifica el RUT o regístralo primero.")
        cleaned_data['cliente'] = cliente

        # Buscar vehículo
        try:
            vehiculo = Vehiculo.objects.get(patente=vehiculo_patente)
            if vehiculo.estado != 'disponible':
                raise ValidationError("El vehículo no está disponible.")
            cleaned_data['vehiculo'] = vehiculo
        except Vehiculo.DoesNotExist:
            raise ValidationError("Vehículo no encontrado.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo_alquiler = self.cleaned_data['tipo_alquiler']
        last_alquiler = Alquiler.objects.order_by('-id').first()
        new_number = 'C1' if tipo_alquiler == 'contrato' else 'R1'
        if last_alquiler:
            last_num = int(last_alquiler.numero_alquiler[1:])
            new_number = f"{tipo_alquiler[0].upper()}{last_num + 1}"  # Asegura prefijo en mayúscula
        instance.numero_alquiler = new_number
        instance.cliente = self.cleaned_data['cliente']
        instance.vehiculo = self.cleaned_data['vehiculo']
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = ['vehiculo', 'marca_modelo', 'kilometraje', 'tipo_mantenimiento', 'fecha_ingreso', 'fecha_salida', 'nivel_combustible', 'encargado', 'observaciones', 'taller']
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'marca_modelo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_mantenimiento': forms.Select(attrs={'class': 'form-select'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nivel_combustible': forms.Select(choices=NIVEL_COMBUSTIBLE, attrs={'class': 'form-select'}),
            'encargado': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'taller': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'vehiculo': 'Vehículo',
            'marca_modelo': 'Marca / Modelo',
            'kilometraje': 'Kilometraje',
            'tipo_mantenimiento': 'Tipo de Mantenimiento',
            'fecha_ingreso': 'Fecha de Ingreso',
            'fecha_salida': 'Fecha de Salida',
            'nivel_combustible': 'Nivel de Combustible',
            'encargado': 'Encargado',
            'observaciones': 'Observaciones',
            'taller': 'Taller',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo'].queryset = Vehiculo.objects.all()
        self.fields['vehiculo'].label_from_instance = lambda obj: obj.patente
        if self.instance and self.instance.pk:
            self.fields['marca_modelo'].initial = f"{self.instance.vehiculo.marca.nombre if self.instance.vehiculo.marca else 'Sin marca'} / {self.instance.vehiculo.modelo.nombre if self.instance.vehiculo.modelo else 'Sin modelo'}"
        self.fields['marca_modelo'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        fecha_salida = cleaned_data.get('fecha_salida')
        kilometraje = cleaned_data.get('kilometraje')

        if fecha_ingreso and fecha_salida and fecha_salida < fecha_ingreso:
            self.add_error('fecha_salida', "La fecha de salida no puede ser anterior a la fecha de ingreso.")
        if kilometraje is not None and not (0 <= kilometraje <= 500000):
            self.add_error('kilometraje', "El kilometraje debe estar entre 0 y 500,000.")
        return cleaned_data

class TrabajoRealizadoForm(forms.ModelForm):
    class Meta:
        model = TrabajoRealizado
        fields = ['codigo', 'descripcion', 'unidades', 'valor_unidad']
        labels = {
            'codigo': 'Código',
            'descripcion': 'Descripción',
            'unidades': 'Unidades',
            'valor_unidad': 'Valor Unitario',
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'unidades': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_unidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        unidades = cleaned_data.get('unidades')
        valor_unidad = cleaned_data.get('valor_unidad')

        if unidades is not None and unidades <= 0:
            self.add_error('unidades', "Las unidades deben ser mayores a 0.")
        if valor_unidad is not None and valor_unidad < 0:
            self.add_error('valor_unidad', "El valor unitario no puede ser negativo.")
        return cleaned_data

TrabajoRealizadoFormSet = inlineformset_factory(
    Mantenimiento,
    TrabajoRealizado,
    form=TrabajoRealizadoForm,
    extra=1,
    can_delete=True
)

class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = ['producto', 'unidades', 'valor_unidad']
        labels = {
            'producto': 'Producto',
            'unidades': 'Unidades',
            'valor_unidad': 'Valor Unitario',
        }
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'unidades': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_unidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        unidades = cleaned_data.get('unidades')
        valor_unidad = cleaned_data.get('valor_unidad')

        if not producto:
            self.add_error('producto', "Debe seleccionar un producto.")
        if unidades is not None and unidades <= 0:
            self.add_error('unidades', "Las unidades deben ser mayores a 0.")
        if valor_unidad is not None and valor_unidad < 0:
            self.add_error('valor_unidad', "El valor unitario no puede ser negativo.")
        return cleaned_data

RepuestoFormSet = inlineformset_factory(
    Mantenimiento,
    Repuesto,
    form=RepuestoForm,
    fields=['producto', 'unidades', 'valor_unidad'],
    extra=1,
    can_delete=True
)

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'codigo_referencia', 'valor_unitario', 'unidades', 'proveedor', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'codigo_referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidades': forms.NumberInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'codigo_referencia': 'Código de Referencia',
            'valor_unitario': 'Valor Unitario',
            'unidades': 'Unidades en Stock',
            'proveedor': 'Proveedor',
            'descripcion': 'Descripción',
        }

    def clean(self):
        cleaned_data = super().clean()
        unidades = cleaned_data.get('unidades')
        valor_unitario = cleaned_data.get('valor_unitario')

        if unidades is not None and unidades < 0:
            self.add_error('unidades', "Las unidades no pueden ser negativas.")
        if valor_unitario is not None and valor_unitario <= 0:
            self.add_error('valor_unitario', "El valor unitario debe ser mayor a 0.")
        return cleaned_data

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'telefono', 'correo', 'direccion', 'contacto']
        labels = {
            'nombre': 'Nombre',
            'telefono': 'Teléfono',
            'correo': 'Correo Electrónico',
            'direccion': 'Dirección',
            'contacto': 'Persona de Contacto',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }

class IngresoArticuloForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'cantidad', 'notas']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad a Ingresar',
            'notas': 'Notas',
        }

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')

        if cantidad is not None and cantidad <= 0:
            self.add_error('cantidad', "La cantidad debe ser mayor a 0.")
        return cleaned_data

class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = [
            'rut', 'nombre_legal', 'nombre_comercial', 'giro', 'direccion',
            'region', 'ciudad', 'contacto', 'telefono', 'correo_electronico',
            'numero_interno', 'servicios', 'horario_atencion'
        ]
        labels = {
            'rut': 'RUT',
            'nombre_legal': 'Nombre Legal de la Empresa',
            'nombre_comercial': 'Nombre Comercial',
            'giro': 'Giro o Rubro',
            'direccion': 'Dirección',
            'region': 'Región',
            'ciudad': 'Ciudad',
            'contacto': 'Contacto',
            'telefono': 'Teléfono',
            'correo_electronico': 'Correo Electrónico de Contacto',
            'numero_interno': 'Número Interno',
            'servicios': 'Servicios que Ofrece',
            'horario_atencion': 'Horario de Atención',
        }
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'nombre_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'giro': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: taller@ejemplo.com'}),
            'numero_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'servicios': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'horario_atencion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get('rut')
        nombre_legal = cleaned_data.get('nombre_legal')
        nombre_comercial = cleaned_data.get('nombre_comercial')

        if not rut or not rut.strip():
            self.add_error('rut', "El RUT es obligatorio.")
        else:
            try:
                validar_rut(rut)  # Validar formato y dígito verificador del RUT
            except ValidationError as e:
                self.add_error('rut', str(e))
        if not nombre_legal or not nombre_legal.strip():
            self.add_error('nombre_legal', "El nombre legal es obligatorio.")
        if not nombre_comercial or not nombre_comercial.strip():
            self.add_error('nombre_comercial', "El nombre comercial es obligatorio.")
        return cleaned_data