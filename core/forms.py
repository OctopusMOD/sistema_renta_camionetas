from django import forms
from django.forms import inlineformset_factory
from .models import (
    Vehiculo, Cliente, Alquiler, Mantenimiento, Taller,
    TrabajoRealizado, RepuestoUtilizado, DocumentoAdjunto,
    LineaTrabajo, RepuestoUsado, Repuesto
)

# Formulario Vehículo
class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'anio', 'patente', 'estado']

# Formulario Alquiler
class AlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ['vehiculo', 'cliente', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulario Mantenimiento
class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = [
            'vehiculo', 'tipo', 'kilometraje_ingreso', 'nivel_combustible',
            'taller', 'fecha_ingreso', 'fecha_fin', 'estado', 'observaciones', 'encargado'
        ]
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_fin and fecha_ingreso and fecha_fin < fecha_ingreso:
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha de ingreso.")
        return cleaned_data

# Formulario Trabajo realizado
class TrabajoRealizadoForm(forms.ModelForm):
    class Meta:
        model = TrabajoRealizado
        fields = ['descripcion', 'costo']

TrabajoFormSet = inlineformset_factory(
    Mantenimiento, TrabajoRealizado,
    form=TrabajoRealizadoForm, extra=1, can_delete=True
)

# Formulario Repuesto Utilizado
class RepuestoUtilizadoForm(forms.ModelForm):
    class Meta:
        model = RepuestoUtilizado
        fields = ['nombre', 'costo', 'desde_inventario']

RepuestoUtilizadoFormSet = inlineformset_factory(
    Mantenimiento, RepuestoUtilizado,
    form=RepuestoUtilizadoForm, extra=1, can_delete=True
)

# Formulario Documento Adjunto
class DocumentoAdjuntoForm(forms.ModelForm):
    class Meta:
        model = DocumentoAdjunto
        fields = ['archivo']

DocumentoFormSet = inlineformset_factory(
    Mantenimiento, DocumentoAdjunto,
    form=DocumentoAdjuntoForm, extra=1, can_delete=True
)

# Formulario Línea de Trabajo
class LineaTrabajoForm(forms.ModelForm):
    class Meta:
        model = LineaTrabajo
        fields = ['descripcion', 'cantidad', 'valor_unitario']

LineaTrabajoFormSet = inlineformset_factory(
    Mantenimiento, LineaTrabajo,
    form=LineaTrabajoForm, extra=1, can_delete=True
)

# Formulario Repuesto desde Inventario
class RepuestoUsadoForm(forms.ModelForm):
    class Meta:
        model = RepuestoUsado
        fields = ['repuesto', 'cantidad_usada']

RepuestoUsadoFormSet = inlineformset_factory(
    Mantenimiento, RepuestoUsado,
    form=RepuestoUsadoForm, extra=1, can_delete=True
)
