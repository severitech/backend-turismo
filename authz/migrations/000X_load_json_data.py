from django.db import migrations
import json
import os

def load_json_data(apps, schema_editor):
    # Ajusta el nombre y la ruta de tu archivo JSON aquí
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'usuarios_seed.json')
    json_path = os.path.abspath(json_path)
    if not os.path.exists(json_path):
        print(f"Archivo JSON no encontrado: {json_path}")
        return
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    Usuario = apps.get_model('authz', 'Usuario')
    Rol = apps.get_model('authz', 'Rol')
    for entry in data:
        # Crea o actualiza el usuario
        usuario, created = Usuario.objects.get_or_create(email=entry['email'], defaults={
            'nombres': entry.get('nombres', ''),
            'apellidos': entry.get('apellidos', ''),
            'telefono': entry.get('telefono', ''),
            'estado': entry.get('estado', 'ACTIVO'),
            'password_hash': entry.get('password_hash', ''),
        })
        # Asigna roles si existen
        for rol_nombre in entry.get('roles', []):
            rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
            usuario.roles.add(rol)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('authz', '0002_seed_roles'),
    ]
    operations = [
        migrations.RunPython(load_json_data, noop),
    ]
