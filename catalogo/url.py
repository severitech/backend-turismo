from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('servicios/', views.servicio_list, name='servicio_lista'),  # Lista de servicios
    path('servicio/<int:pk>/', views.servicio_detail, name='servicio_detalles'),  # Detalles de un servicio
    path('servicio/nuevo/', views.servicio_create, name='servicio_crear'),  # Crear un servicio
    path('servicio/<int:pk>/editar/', views.servicio_edit, name='servicio_editar'),  # Editar servicio
    path('servicio/<int:pk>/eliminar/', views.servicio_delete, name='servicio_eliminar'),  # Eliminar servicio
]
