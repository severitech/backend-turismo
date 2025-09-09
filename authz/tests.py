from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from authz.models import Usuario, Rol

User = get_user_model()

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        # Create Usuario with proper password hash
        from django.contrib.auth.hashers import make_password
        self.usuario = Usuario.objects.create(
            nombre='Test User',
            email='test@example.com',
            password_hash=make_password('testpass123'),
            estado='ACTIVO'
        )
        self.client_role, _ = Rol.objects.get_or_create(nombre='CLIENTE')
        self.admin_role, _ = Rol.objects.get_or_create(nombre='ADMIN')

    def test_login_with_valid_credentials(self):
        """Probar login con credenciales válidas"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        """Probar login con credenciales inválidas"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Probar login sin campos requeridos"""
        url = reverse('login')
        data = {
            'email': 'test@example.com'
            # falta password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_usuario_me_endpoint_authenticated(self):
        """Probar endpoint /me con usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        url = '/api/usuarios/me/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_usuario_me_endpoint_unauthenticated(self):
        """Probar endpoint /me sin autenticación"""
        url = '/api/usuarios/me/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inhabilitar_cuenta(self):
        """Probar inhabilitar cuenta propia"""
        self.client.force_authenticate(user=self.user)
        url = '/api/usuarios/inhabilitar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el usuario fue marcado como inactivo
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.estado, 'INACTIVO')

    def test_reactivar_cuenta_sin_permisos(self):
        """Probar reactivar cuenta sin permisos de admin"""
        self.client.force_authenticate(user=self.user)
        
        # Crear otro usuario inactivo
        inactive_user = Usuario.objects.create(
            nombre='Inactive User',
            email='inactive@example.com',
            password_hash='hashed',
            estado='INACTIVO'
        )
        
        url = f'/api/usuarios/{inactive_user.pk}/reactivar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reactivar_cuenta_con_permisos_admin(self):
        """Probar reactivar cuenta con permisos de admin"""
        # Asignar rol admin al usuario
        self.usuario.roles.add(self.admin_role)
        self.client.force_authenticate(user=self.user)
        
        # Crear otro usuario inactivo
        inactive_user = Usuario.objects.create(
            nombre='Inactive User',
            email='inactive@example.com',
            password_hash='hashed',
            estado='INACTIVO'
        )
        
        url = f'/api/usuarios/{inactive_user.pk}/reactivar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el usuario fue reactivado
        inactive_user.refresh_from_db()
        self.assertEqual(inactive_user.estado, 'ACTIVO')
