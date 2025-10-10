# core/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = pago
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        monto = cleaned_data.get("monto")
        fecha_pago = cleaned_data.get("fecha_pago")

        if monto is not None and monto <= 0:
            raise ValidationError("El monto debe ser mayor que cero.")

        if not fecha_pago:
            raise ValidationError("La fecha de pago es obligatoria.")

        return cleaned_data
