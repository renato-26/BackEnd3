# core/scoping.py
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import FieldError

# ---- DRF opcional (no romper si DRF no está instalado) ----------------------
try:
    from rest_framework.filters import BaseFilterBackend  # type: ignore
    from rest_framework.request import Request  # type: ignore
    _DRF = True
except Exception:
    _DRF = False

    class BaseFilterBackend:  # no-op para que el import no falle
        def filter_queryset(self, request, queryset, view):
            return queryset

    class Request:  # shim mínimo para type hints
        pass
# -----------------------------------------------------------------------------

# Modelo real de empleado en tu proyecto
SCOPING_EMPLOYEE_MODEL = "core.empleado"

# Claves que podemos leer desde el propio objeto empleado
SCOPING_EMPLOYEE_KEYS = ("empleado", "empresa", "sucursal", "departamento")

# Rutas candidatas para filtrar en cualquier queryset (directas y anidadas)
SCOPING_PATHS = (
    # directas
    "empleado",
    "empresa",
    "sucursal",
    "departamento",
    # 1 salto
    "contrato__empleado",
    "contrato__empresa",
    "contrato__sucursal",
    "liquidacion__empleado",
    "liquidacion__empresa",
    "liquidacion__sucursal",
    # 2 saltos (pago -> liquidacion -> contrato -> empleado)
    "liquidacion__contrato__empleado",
    "liquidacion__contrato__empresa",
    "liquidacion__contrato__sucursal",
)

def _get_employee_for_user(user):
    """Devuelve el objeto empleado enlazado al user, o None."""
    if not user or isinstance(user, AnonymousUser):
        return None
    try:
        Empleado = apps.get_model(SCOPING_EMPLOYEE_MODEL)
        # select_related solo para las claves que existan en el modelo
        sr = []
        for k in SCOPING_EMPLOYEE_KEYS:
            if k == "empleado":
                continue
            try:
                Empleado._meta.get_field(k)
                sr.append(k)
            except Exception:
                pass
        return Empleado.objects.select_related(*sr).get(user=user)
    except Exception:
        return None

def _value_from_employee(empleado, key):
    """Valor a usar según la base del path (empleado/empresa/sucursal/...)."""
    if key == "empleado":
        return empleado
    return getattr(empleado, key, None)

def _apply_scope(qs, empleado):
    """
    Intenta aplicar el primer path válido de SCOPING_PATHS sobre qs.
    Si el path termina en '__empleado' o es 'empleado', usa el objeto empleado.
    Para 'empresa'/'sucursal'/'departamento' usa ese atributo de empleado.
    """
    if not empleado:
        return qs
    for path in SCOPING_PATHS:
        base = path.split("__")[-1]
        val = _value_from_employee(empleado, base)
        if val is None:
            continue
        try:
            return qs.filter(**{path: val})
        except FieldError:
            continue
        except Exception:
            continue
    return qs  # no encontró path aplicable; devuelve queryset tal cual

# -------------------- DRF backends / mixin -----------------------------------

class ScopedFilterBackend(BaseFilterBackend):
    """FilterBackend DRF (no-op si DRF no está)."""
    def filter_queryset(self, request: Request, queryset, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False) or getattr(user, "is_superuser", False):
            return queryset
        empleado = _get_employee_for_user(user)
        return _apply_scope(queryset, empleado)

class ScopedQuerysetMixin:
    """Mixin usable en ViewSets/GenericAPIView (y seguro sin DRF)."""
    def get_queryset(self):
        qs = super().get_queryset()
        request = getattr(self, "request", None)
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False) or getattr(user, "is_superuser", False):
            return qs
        empleado = _get_employee_for_user(user)
        return _apply_scope(qs, empleado)
