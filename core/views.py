from rest_framework.viewsets import ModelViewSet
from core.scoping import ScopedFilterBackend

class DispositivoViewSet(ModelViewSet):
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
    filter_backends = [ScopedFilterBackend]  # añade, sin quitar tus otros filtros

