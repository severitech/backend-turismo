from rest_framework import serializers
from .models import Categoria, Servicio

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"  # expone todos los campos del modelo

class ServicioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source="categoria.nombre", read_only=True
    )
    
    # Asegúrate de que el campo categoria reciba el ID y no un objeto completo
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())

    class Meta:
        model = Servicio
        fields = "__all__"
