from .models import Categoria
from rest_framework import viewsets, permissions
from serializers import CategoriaSerializer
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all() 
    permission_classes = [permissions.AllowAny] #cualquier cliente puede solicitar datos a mi servidor
    serializer_class = CategoriaSerializer
