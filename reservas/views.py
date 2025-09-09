from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Reserva, Visitante, ReservaVisitante
from .serializers import ReservaSerializer, VisitanteSerializer, ReservaVisitanteSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().select_related("usuario","cupon").prefetch_related("detalles")
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["estado", "usuario"]
    ordering_fields = ["fecha_inicio", "created_at", "total"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            # Verificar si el usuario tiene rol ADMIN
            try:
                from authz.models import Usuario
                usuario = Usuario.objects.get(email=self.request.user.email)
                if usuario.roles.filter(nombre="ADMIN").exists():
                    return qs  # Admins pueden ver todas las reservas
                # Usuarios regulares solo ven sus propias reservas
                return qs.filter(usuario=usuario)
            except Usuario.DoesNotExist:
                pass
        return qs.none()

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "apellido", "documento", "email"]
    ordering_fields = ["nombre", "apellido", "created_at"]

class ReservaVisitanteViewSet(viewsets.ModelViewSet):
    queryset = ReservaVisitante.objects.all()
    serializer_class = ReservaVisitanteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["reserva", "estado", "es_titular"]