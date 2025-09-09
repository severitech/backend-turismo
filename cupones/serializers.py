from rest_framework import serializers
from .models import Cupon

class CuponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupon
        fields = ["id", "codigo", "tipo", "valor", "fecha_inicio", "fecha_fin", "estado", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_valor(self, value):
        """Validar que el valor sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El valor debe ser mayor a 0")
        return value

    def validate(self, attrs):
        """Validar fechas"""
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        return attrs