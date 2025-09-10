from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Reserva, Visitante, ReservaVisitante
from .serializers import ReservaSerializer, VisitanteSerializer, ReservaVisitanteSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().select_related("usuario", "cupon").prefetch_related("detalles")
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_user_roles(self):
        user = self.request.user
        # Verifica que el usuario tenga el atributo 'roles'
        if hasattr(user, 'roles'):
            return list(user.roles.values_list('nombre', flat=True))  # type: ignore
        return []

    def get_queryset(self):  # type: ignore
        roles = self.get_user_roles()
        user = self.request.user
        if 'ADMIN' in roles or 'OPERADOR' in roles:
            return Reserva.objects.all().select_related("usuario", "cupon").prefetch_related("detalles")
        if 'CLIENTE' in roles:
            return Reserva.objects.filter(usuario=user).select_related("usuario", "cupon").prefetch_related("detalles")
        return Reserva.objects.none()

    def perform_create(self, serializer):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR', 'CLIENTE']):
            raise PermissionDenied("No tienes permisos para crear reservas.")
        if 'CLIENTE' in roles:
            serializer.save(usuario=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        roles = self.get_user_roles()
        if not any(r in roles for r in ['ADMIN', 'OPERADOR']):
            raise PermissionDenied("No tienes permisos para actualizar reservas.")
        serializer.save()

    def perform_destroy(self, instance):
        roles = self.get_user_roles()
        if 'ADMIN' not in roles:
            raise PermissionDenied("Solo el rol ADMIN puede eliminar reservas.")
        instance.delete()
    # ...existing code...

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReservaVisitanteViewSet(viewsets.ModelViewSet):
    queryset = ReservaVisitante.objects.all()
    serializer_class = ReservaVisitanteSerializer
    permission_classes = [permissions.IsAuthenticated]