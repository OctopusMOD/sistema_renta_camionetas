from django import forms
from django.forms import inlineformset_factory
from .models import Vehiculo, Cliente, Alquiler, Mantenimiento, LineaTrabajo, Taller

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'anio', 'placa', 'estado']

class AlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ['vehiculo', 'cliente', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = ['vehiculo', 'taller', 'fecha_inicio', 'fecha_fin', 'estado']  # Excluimos 'descripcion' si no se usa
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return cleaned_data

class LineaTrabajoForm(forms.ModelForm):
    class Meta:
        model = LineaTrabajo
        fields = ['descripcion', 'cantidad', 'valor_unitario']

LineaTrabajoFormSet = inlineformset_factory(
    Mantenimiento,
    LineaTrabajo,
    form=LineaTrabajoForm,
    fields=['descripcion', 'cantidad', 'valor_unitario'],
    extra=1,
    can_delete=True
)