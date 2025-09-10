import json
from django.db import migrations

def load_initial_users(apps, schema_editor):
    Usuario = apps.get_model('authz', 'Usuario')
    Rol = apps.get_model('authz', 'Rol')
    RolUsuario = apps.get_model('authz', 'RolUsuario')
    with open('authz/initial_users.json', encoding='utf-8') as f:
        data = json.load(f)
        for user_data in data:
            roles = user_data.pop('roles', [])
            usuario = Usuario.objects.create(**user_data)
            for rol_nombre in roles:
                rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
                RolUsuario.objects.get_or_create(usuario=usuario, rol=rol)

class Migration(migrations.Migration):
    dependencies = [
        ('authz', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_initial_users),
    ]
