from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Cupon
from .serializers import CuponSerializer

class CuponViewSet(viewsets.ModelViewSet):
    queryset = Cupon.objects.all()
    serializer_class = CuponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar cupones por estado y fechas válidas para usuarios no admin"""
        qs = super().get_queryset()
        
        # Solo admins pueden ver todos los cupones
        if hasattr(self.request.user, 'email'):
            try:
                from authz.models import Usuario
                usuario = Usuario.objects.get(email=self.request.user.email)
                if usuario.roles.filter(nombre="ADMIN").exists():
                    return qs
            except Usuario.DoesNotExist:
                pass
        
        # Para usuarios regulares, solo mostrar cupones activos y vigentes
        now = timezone.now()
        return qs.filter(
            estado=True,
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        )

    @action(detail=True, methods=["post"], url_path="validar")
    def validar(self, request, pk=None):
        """Validar si un cupón es aplicable"""
        cupon = self.get_object()
        
        if not cupon.estado:
            return Response({"detail": "Cupón inactivo.", "valido": False}, status=400)
        
        now = timezone.now()
        if cupon.fecha_inicio and cupon.fecha_inicio > now:
            return Response({"detail": "Cupón aún no vigente.", "valido": False}, status=400)
            
        if cupon.fecha_fin and cupon.fecha_fin < now:
            return Response({"detail": "Cupón expirado.", "valido": False}, status=400)
        
        return Response({
            "detail": "Cupón válido.",
            "valido": True,
            "tipo": cupon.tipo,
            "valor": cupon.valor
        })

    @action(detail=True, methods=["post"], url_path="desactivar", permission_classes=[permissions.IsAuthenticated])
    def desactivar(self, request, pk=None):
        """Permite a un admin desactivar un cupón"""
        try:
            from authz.models import Usuario
            usuario_admin = Usuario.objects.get(email=request.user.email)
            if not usuario_admin.roles.filter(nombre="ADMIN").exists():
                return Response({"detail": "No tienes permisos para realizar esta acción."}, status=403)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=404)
        
        cupon = self.get_object()
        cupon.estado = False
        cupon.save()
        
        return Response({"detail": "Cupón desactivado correctamente."}, status=200)
