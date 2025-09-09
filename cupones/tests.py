from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from cupones.models import Cupon
from authz.models import Usuario, Rol

User = get_user_model()

class CuponTestCase(APITestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.usuario = Usuario.objects.create(
            nombre='Test User',
            email='test@example.com',
            password_hash='hashed_password',
            estado='ACTIVO'
        )
        self.admin_role, _ = Rol.objects.get_or_create(nombre='ADMIN')
        
        # Crear cupón de prueba
        self.cupon = Cupon.objects.create(
            codigo='TEST10',
            tipo='PORCENTAJE',
            valor=10.00,
            fecha_inicio=timezone.now() - timedelta(days=1),
            fecha_fin=timezone.now() + timedelta(days=30),
            estado=True
        )

    def test_listar_cupones_usuario_regular(self):
        """Usuarios regulares solo ven cupones activos y vigentes"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/cupones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_validar_cupon_valido(self):
        """Probar validación de cupón válido"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/cupones/{self.cupon.pk}/validar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valido'])

    def test_validar_cupon_expirado(self):
        """Probar validación de cupón expirado"""
        # Crear cupón expirado
        cupon_expirado = Cupon.objects.create(
            codigo='EXPIRED',
            tipo='FIJO',
            valor=50.00,
            fecha_inicio=timezone.now() - timedelta(days=10),
            fecha_fin=timezone.now() - timedelta(days=1),
            estado=True
        )
        
        self.client.force_authenticate(user=self.user)
        url = f'/api/cupones/{cupon_expirado.pk}/validar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valido'])

    def test_desactivar_cupon_sin_permisos(self):
        """Usuario sin permisos no puede desactivar cupón"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/cupones/{self.cupon.pk}/desactivar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_desactivar_cupon_con_permisos_admin(self):
        """Admin puede desactivar cupón"""
        self.usuario.roles.add(self.admin_role)
        self.client.force_authenticate(user=self.user)
        url = f'/api/cupones/{self.cupon.pk}/desactivar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el cupón fue desactivado
        self.cupon.refresh_from_db()
        self.assertFalse(self.cupon.estado)
